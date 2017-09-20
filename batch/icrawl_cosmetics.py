
from datetime import datetime
from datetime import time
from datetime import timedelta
# from django.core.files import File
import glob, os
import pickle
import urllib
import requests
from urllib.parse import urlparse
import re
from requests_ntlm import HttpNtlmAuth
from pandas import Series, DataFrame
import pandas as pd
from bs4 import BeautifulSoup

from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.connections import connections
from elasticsearch.client import IndicesClient
from elasticsearch.helpers import bulk

from batch.crawler import Crawler as Crawler
import batch.models as models
import batch.elastic as elastic
from helper.helpervariable import *




class CosmeticsCrawler(Crawler):

    def __init__(self, site, nrpages):
        self.site = site
        self.nrpages = nrpages


    def get_pagination_links(self, sub_site):
        include_url = urlparse(sub_site).scheme+"://"+urlparse(sub_site).netloc
        links = set()
        url = sub_site
        page_nr = 0
        page_size = 10
        link_count = 0
        while url != None and link_count < self.nrpages:
            # bs = batch_crawl.read_page(url)
            print(url)
            bs = Crawler.read_page(url)
            box_1_tag = bs.find("div", class_="box_1")
            for link_tag in box_1_tag.findAll("a", href=re.compile("^(/|.*"+include_url+")")):
                if link_tag.attrs['href'] is not None:
                    if link_tag.attrs['href'] not in links:
                        if link_tag.attrs['href'].startswith('/'):
                            link = include_url+link_tag.attrs['href']
                        else:
                            link = link_tag.attrs['href']
                        links.add(link)
                        link_count = link_count + 1
            result_count_tag = bs.find("span", class_="result_count")
            if result_count_tag != None:
                result_count_list = result_count_tag.text.split()
                result_count = int(float(result_count_list[4]))
            else:
                result_count = page_size
            navigation_tag = bs.find(id="navigation")
            if navigation_tag != None:
                next_tag = navigation_tag.find("span", class_="next")
                if next_tag != None:
                    next_url = include_url + next_tag.find("a").attrs['href']
                else:
                    next_url = None
            else:
                page_nr = page_nr + 1
                if page_nr * page_size > result_count:
                    next_url = None
                else:
                    next_url = sub_site + '/(offset)/{}'.format(page_nr)
            url = next_url
        return links


    def scrape_page_map(self, sub_site, url, bs):
        id = url
        pagemap             = models.PageMap()
        pagemap.page_id     = id
        pagemap.site        = self.site
        pagemap.sub_site    = sub_site
        pagemap.url         = url

        # get posted date
        try:
            pagemap.posted_date = datetime.today()
            author_info_tag = bs.find("div", class_="author_info")
            published = author_info_tag.find('p', class_='date').text
            pagemap.posted_date = datetime.strptime(published, '%d-%b-%Y')
        except:
            pass
        try:
            box_1_tag = bs.find("div", class_="box_1")
            product_info_bar_tag = box_1_tag.find("div", class_="product_info_bar")
            published = re.search(r'([0-9]{2}-[a-z,A-Z]{3}-[0-9]{4})', product_info_bar.text, re.MULTILINE)
            pagemap.posted_date = datetime.strptime(published.group(0), '%d-%b-%Y')
        except:
            pass
        # get page
        try:
            pagemap.page        = bs.get_text()
            box_1_tag = bs.find("div", class_="box_1")
            pagemap.page = box_1_tag.text
            product_main_text_tag = box_1_tag.find("div", class_="product_main_text")
            if product_main_text_tag != None:
                pagemap.page = product_main_text_tag.text
            else:
                story_tag = box_1_tag.find("div", class_="story")
                pagemap.page = story_tag.text
        except:
            pass
        # get title
        try:
            if bs.title != None:
                pagemap.title   = bs.title.text
            else:
                pagemap.title   = ''
            box_1_tag = bs.find("div", class_="box_1")
            pagemap.title = box_1_tag.find("h1").text
        except:
            pass
        # get section
        try:

            box_2_tag = bs.find("div", class_="box_2")

            box_2_tag = box_2_tag.text.strip('\t\n\r\l')

            if box_2_tag:
            # if box_2_tag != None:

                pagemap.section = box_2_tag

            else:

                pagemap.section = str('_')

        except:
            pass
        with open('file.txt', 'a') as f:
            print(pagemap.section, file = f)
        data = elastic.convert_for_bulk(pagemap, 'update')
        return data


    def crawl_cosmetic(self, scrape_choices, nrpages):
        cosmetic = CosmeticsCrawler('Cosmetics', nrpages)
        sub_sites = {}
        if len(scrape_choices) == 0:
            sub_sites.add(site)
    #   for site in ['http://www.cosmeticsdesign.com/', 'http://www.cosmeticsdesign-europe.com/', 'http://www.cosmeticsdesign-asia.com/']:
        for site_url in ['http://www.cosmeticsdesign.com/']:
            for scrape_choice in list(scrape_choices):
                if scrape_choice == 'product':
                    sub_sites['Skin-care'] = site_url + '/Product-Categories/Skin-Care'
                    sub_sites['Hair-care'] = site_url +'/Product-Categories/Hair-Care'
                if scrape_choice == 'market':
                    sub_sites['Market-Trends'] = site_url + '/Market-Trends'
                    sub_sites['Brand-Innovation'] = site_url +'/Brand-Innovation'
        print(len(sub_sites))
        for sub_site, sub_site_url in sub_sites.items():
            links = cosmetic.get_pagination_links(sub_site_url)
            for link in links:
                bs = Crawler.read_page(link)
                cosmetic.pages.add(link)
                data = cosmetic.scrape_page_map(sub_site, link, bs)
                cosmetic.bulk_data.append(data)

        bulk(models.client, actions=cosmetic.bulk_data, stats_only=True)

'''
if __name__ == '__main__':
    hv = HelperVariable()
    scrape_choices = ('product', 'market' ) # 'product', 'market'
    batch_crawl = CosmeticsCrawler(hv.COS_DESIGN_SITE_URL, hv.NRPAGES)

    # scrape_choices = (('market', 'Market'), ('business', 'Business'), ('product', 'Product'), ('events', 'Events'),
    #                 ('publications', 'Publications'), ('blog', 'Blog'))

    batch_crawl.crawl_cosmetic(scrape_choices, nrpages=1)


'''
