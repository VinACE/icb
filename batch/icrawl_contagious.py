
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

from batch.crawler import Crawler
import batch.models as models
import batch.elastic as elastic
from helper.helpervariable import *



class ContagiousCrawler(Crawler):

    def __init__(self, site, nrpages):
        # Instantiating HelperVariable
        self.hv = HelperVariable()
        self.site = site
        self.nrpages = nrpages

    def get_pagination_links_blog(self, sub_site):
        include_url = urlparse(sub_site).scheme + "://" + urlparse(sub_site).netloc
        links = set()
        url = sub_site
        page_nr = 0
        page_size = 10
        link_count = 0
        while url != None and link_count < self.nrpages:
            bs = Crawler.read_page(url)

            # blog_posts_tag = bs.find("section", id_ = "pub-list") # "div", class_="blog-posts")
            blog_posts_tag = bs.find("div", id="page-container")

            for link_tag in blog_posts_tag.findAll("a", href=re.compile("^(/|.*" + include_url + ")")):
                if link_tag.attrs['href'] is not None:
                    if link_tag.attrs['href'] not in links:
                        if link_tag.attrs['href'].startswith('/'):
                            link = include_url + link_tag.attrs['href']
                        else:
                            link = link_tag.attrs['href']
                        links.add(link)
                        link_count = link_count + 1
            navigation_tag = bs.find("div", id="pagination-parts") # bs.find("nav", class_="nav-below")
            if navigation_tag != None:
                next_tag = navigation_tag.find("span", class_="next")
                if next_tag != None:
                    print(type(next_tag))
                    # print(next_tag.parent.attrs['href'])
                    next_tag = str(next_tag)
                    print(next_tag)
                    next_url = re.findall('<a href="?\'?([^"\'>]*)', next_tag)
                    # next_url = next_tag.parent.attrs['href']
                    next_url=next_url[0]
                    print(next_url)
                else:
                    next_url = None
            url = include_url + next_url
        return links


    def scrape_page_map(self, sub_site, url, bs):
        id = url
        pagemap = models.PageMap()
        pagemap.page_id = id
        pagemap.site = self.site
        pagemap.sub_site = sub_site
        pagemap.url = url

        # get posted date
        # <span class="entry-date">May 23, 2017</span>
        try:
            pagemap.posted_date = datetime.today()
            entry_date_tag = bs.find("span", class_="entry-date")
            published = entry_date_tag.text
            pagemap.posted_date = datetime.strptime(published, '%B %d, %Y')
        except:
            pass
        # try:
        #    box_1_tag = bs.find("div", class_="box_1")
        #    product_info_bar_tag = box_1_tag.find("div", class_="product_info_bar")
        #    published = re.search(r'([0-9]{2}-[a-z,A-Z]{3}-[0-9]{4})', product_info_bar.text, re.MULTILINE)
        #    pagemap.posted_date = datetime.strptime(published.group(0), '%d-%b-%Y')
        # except:
        #    pass

        # get page
        # <section class="entry-content">
        try:
            pagemap.page = bs.get_text()
            entry_content_tag = bs.find("section", class_="entry-content")
            pagemap.page = entry_content_tag.text
        except:
            pass
        # get title
        # <h1 class="entry-title"></h1>  text
        try:
            if bs.title != None:
                pagemap.title = bs.title.text
            else:
                pagemap.title = ''
            entry_title_tag = bs.find("h1", class_="entry-title")
            pagemap.title = entry_title_tag.text
        except:
            pass
        # get section
        try:
            pagemap.section = sub_site
        except:
            pass

        data = elastic.convert_for_bulk(pagemap, 'update')
        return data


    def crawl_contagious(self, scrape_choices, nrpages):
        contag = ContagiousCrawler('Contagious', nrpages)
        sub_sites = {}
        site_url = self.hv.CONTAGIOUS_SITE_URL
        for scrape_choice in scrape_choices:
            if scrape_choice == 'newsviews':
                sub_sites['blogs'] = site_url + 'blogs/news-and-views'

        for sub_site, sub_site_url in sub_sites.items():

            if sub_site_url == 'https://www.contagious.com/blogs/news-and-views':
                links = contag.get_pagination_links_blog(sub_site_url)

            for link in links:
                bs = Crawler.read_page(link)
                contag.pages.add(link)
                data = contag.scrape_page_map(sub_site, link, bs)
                contag.bulk_data.append(data)
        bulk(models.client, actions=contag.bulk_data, stats_only=True)



'''
if __name__ == '__main__':
    # hv = HelperVariable()
    # batch_crawl = Crawler()

    # scrape_choices = (('market', 'Market'), ('business', 'Business'), ('product', 'Product'), ('events', 'Events'),
    #                 ('publications', 'Publications'), ('blog', 'Blog'))
    scrape_choices = ('newsviews',) # ,'publications','blog',
    contagious_c = ContagiousCrawler('https://www.contagious.com/', nrpages=2)
    contagious_c.crawl_contagious(scrape_choices, nrpages=100)

'''