# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import re
from pymongo import MongoClient
from string import whitespace
CUSTOM_WHITESPACE = (whitespace + "\xa0").replace(" ", "")


class JobParserPipeline:

    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongobase = client.vacancies200721

    def process_item(self, item, spider):
        loc_dict = dict(item)

        if spider.name == "hhru":
            loc_dict['salary_min'], loc_dict['salary_max'], loc_dict['currency'] = self.salary_parse_hh(
                loc_dict['salary'])
        elif spider.name == "superjobru":
            loc_dict['salary_min'], loc_dict['salary_max'], loc_dict['currency'] = self.salary_parse_superjob(
                loc_dict['salary'])
        del loc_dict['salary']

        self.save(self.mongobase[spider.name], loc_dict)
        return item

    def salary_parse_hh(self, salary_str):
        currency, salary_min, salary_max = None, None, None
        salary = str(salary_str)
        salary = salary.replace('-', '').replace("от", "").replace('до', '-').replace(' ', '').replace('\xa0',
                                                                                                           '').replace(
                ' ', '')
        other_text = re.sub('(\d)', '', salary).replace('-', '')
        if ('руб' in other_text) or ('Руб' in other_text) or ('РУБ' in other_text):
            currency = 'руб'
        elif ('usd' in other_text) or ('USD' in other_text):
            currency = 'usd'
        elif ('eur' in other_text) or ('EUR' in other_text):
            currency = 'eur'

        salary = salary.replace(other_text, '')
        if "-" in salary:
            try:
                salary_min = float(salary.split('-')[0])
            except ValueError:
                salary_min = None
            try:
                salary_max = float(salary.split('-')[1])
            except ValueError:
                salary_max = None
        else:
            try:
                salary_min = float(salary)
            except ValueError:
                salary_min = None

        return salary_min, salary_max, currency

    def salary_parse_superjob(self, salary_list):
        currency, salary_min, salary_max = None, None, None
        salary_str, salary_res = '', []
        for salary in salary_list:
            salary = salary.replace('\xa0', '').replace(' ', '')
            salary = salary.replace('от', '').replace('до', '-')
            if ('руб' in salary) or ('Руб' in salary) or ('РУБ' in salary):
                currency = 'руб'
            elif ('usd' in salary) or ('USD' in salary):
                currency = 'usd'
            elif ('eur' in salary) or ('EUR' in salary):
                currency = 'eur'

            salary = re.sub('\D+', '', salary)
            if salary:
                salary_res.append(salary)

        if len(salary_res) > 1:
            try:
                salary_min = float(salary_res[0])
            except ValueError:
                salary_min = None
            try:
                salary_max = float(salary_res[1])
            except ValueError:
                salary_max = None
        elif len(salary_res) == 1:
            try:
                salary_min = float(salary_res[0])
            except ValueError:
                salary_min = None

        return salary_min, salary_max, currency

    def save(self, collection, data):
        update_data = {}
        filter_dict = {}
        for key in data:
            filter_dict[key] = {'$eq': data[key]}
        update_data['$set'] = data
        collection.update_one(filter_dict, update_data, upsert=True)
