
#Доработать паука в имеющемся проекте, чтобы он формировал item по структуре:
#*Наименование вакансии
#*Зарплата от
#*Зарплата до
#*Ссылку на саму вакансию

#*Сайт откуда собрана вакансия
#И складывал все записи в БД(любую)

from pymongo import MongoClient


class JobParserPipeline(object):
    def __init__(self):
        MONGO_URI = 'mongodb://175.17.1.3:27017/'
        MONGO_DATABASE = 'v_db'

        client = MongoClient(MONGO_URI)
        self.mongo_base = client[MONGO_DATABASE]

    def process_item(self, item, spider):
        if spider.name == 'superjob_ru':
            item['salary'] = self.salary_parse_superjob(item['salary'])

        vacancy_name = ''.join(item['name'])

        s_min = item['salary'][0]
        s_max = item['salary'][1]
        s_currency = item['salary'][2]
        v_link = item['vacancy_link']
        s_scraping = item['site_scraping']

        vacancy_json = {
            'v_name': v_name, \
            'salary_min': s_min, \
            'salary_max': s_max, \
            'salary_currency': s_currency, \
            'vacancy_link': v_link, \
            'site_scraping': s_scraping
        }

        collection = self.mongo_base[spider.name]
        collection.insert_one(vacancy_json)
        return vacancy_json

    def salary_parse_superjob(self, salary):
        s_min = None
        s_max = None
        s_currency = None

        for i in range(len(salary)):
            salary[i] = salary[i].replace(u'\xa0', u'')

        if salary[0] == 'до':
            s_max = salary[2]
        elif len(salary) == 3 and salary[0].isdigit():
            s_max = salary[0]
        elif salary[0] == 'от':
            s_min = salary[2]
        elif len(salary) > 3 and salary[0].isdigit():
            s_min = salary[0]
            s_max = salary[2]

        salary_currency = self._get_name_currency(salary[-1])

        result = [
            s_min, \
            s_max, \
            s_currency
        ]
        return result

    def _get_name_currency(self, currency_name):
        c_dict  = {
            'EUR': {'€'}, \
            'RUB': {'₽', 'руб.'}, \
            'USD': {'$'}
        }

        name = None

        for item_name, items_list in c_dict.items():
            if c_name in items_list:
                name = item_name

        return name

# Создать в имеющемся проекте второго паука по сбору вакансий с сайта superjob. Паук должен формировать item'ы по аналогичной структуре и складывать данные также в БД

import scrapy
from scrapy.http import HtmlResponse
from job_parser.items import JobParserItem


class SuperjobSpider(scrapy.Spider):
    name = 'sj_ru'
    allowed_domains = ['superjob.ru']

    def __init__(self, vacancy=None):
        super(SuperjobSpider, self).__init__()
        self.start_urls = [
            f'https://www.superjob.ru/vacancy/search/?keywords={vacancy}'
        ]

    def parse(self, response):
        next_page = response.css('a.f-test-link-dalshe::attr(href)') \
        .extract_first()

        yield response.follow(next_page, callback=self.parse)

        vacancy_items  = response.css(
            'div.f-test-vacancy-item \
            a[class*=f-test-link][href^="/vakansii"]::attr(href)'
        ).extract()

        for vacancy_link in vacancy_items:
            yield response.follow(vacancy_link, self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('h1 ::text').extract()

        salary = response.css(
            'div._3MVeX span[class="_3mfro _2Wp8I ZON4b PlM3e _2JVkc"] ::text'
        ).extract()

        vacancy_link = response.url

        site_scraping = self.allowed_domains[0]

        yield JobParserItem(
            name=name, \
            salary=salary, \
            vacancy_link=vacancy_link, \
            site_scraping=site_scraping
        )
