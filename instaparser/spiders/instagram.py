import scrapy
import re
from scrapy.http import HtmlResponse
import json
from urllib.parse import urlencode
from copy import deepcopy
from instaparser.items import InstaparserItem
from scrapy.loader import ItemLoader
import os
from dotenv import load_dotenv

load_dotenv("//.env")

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_url = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = os.environ.get('INST_LOGIN')
    inst_pswd = os.environ.get('INST_PSWD')
    query_hash_posts = '8c2a529969ee035a5063f2fc8602a0fd'
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    parse_user = ['raikov_workshop', 'ravnovesie_space']

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_url,
            method='POST',
            callback=self.user_parse,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pswd},
            headers={'X-CSRFToken': csrf}
        )

    def user_parse(self, response: HtmlResponse):
        j_data = json.loads(response.text)
        if j_data['authenticated']:
            for user in self.parse_user:
                yield response.follow(
                    f'/{user}',
                    callback=self.followers_parse,
                    cb_kwargs={'username': user}
                )


    def followers_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {'count': 12,
                     'search_surface': 'follow_list_page'}
        url_followers = f'https://i.instagram.com/api/v1/friendships/{user_id}/followers/?{urlencode(variables)}'
        yield response.follow(url_followers,
                              callback=self.user_posts_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables)
                                         },
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )
        url_following = f'https://i.instagram.com/api/v1/friendships/{user_id}/following/?{urlencode(variables)}'
        yield response.follow(url_following,
                              callback=self.user_posts_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'type': 'following',
                                         'variables': deepcopy(variables)
                                         },
                              headers={'User-Agent': 'Instagram 155.0.0.37.107'}
                              )


    def user_posts_parse(self, response: HtmlResponse, username, user_id, type, variables):
        j_data = json.loads(response.text)
        users = j_data.get('users')

        for user in users:
            loader = ItemLoader(item=InstaparserItem(), response=response)
            loader.add_value('parent_name', username)
            loader.add_value('parent_id', user_id)
            loader.add_value('user_id', user.get('pk'))
            loader.add_value('name', user.get('full_name'))
            loader.add_value('photo', user.get('profile_pic_url'))
            loader.add_value('type', type)
            yield loader.load_item()

        next_page = j_data.get('next_max_id')

        if next_page:
            variables['max_id'] = next_page
            url = f'https://i.instagram.com/api/v1/friendships/{user_id}/{type}/?{urlencode(variables)}'

            yield response.follow(url,
                                headers={'User-Agent': 'Instagram 155.0.0.37.107'},
                                callback=self.user_posts_parse,
                                cb_kwargs={'username': username,
                                           'user_id': user_id,
                                           'type': type,
                                           'variables': deepcopy(variables)}
                                 )

    #Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')


    #Получаем id желаемого пользователя
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')