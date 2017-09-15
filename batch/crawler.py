
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

'''
import app.models as models
import app.elastic as elastic
import app.survey as survey
'''
si_sites = {
    'gci': {
        'site_url': 'http://www.gcimagazine.com/',
        'sub_sites': {
            'gci': 'http://www.gcimagazine.com/'},
    },
}


class Crawler(object):
    site_name = ''
    pages = set()
    bulk_data = []
    nrpages = 50

    '''
    def __init__(self, site, nrpages):
        self.site = site
        self.nrpages = nrpages
    '''
    # read the content of a page into BeautifulSoup
    # def read_page(self, url):
    def read_page(url):

        bs = BeautifulSoup('')
        try:
            print("read_page: scraping url ", url)
            html = urllib.request.urlopen(url)
            bs = BeautifulSoup(html.read(), "lxml")
            [script.decompose() for script in bs("script")]
            print("Read page")
        except:
            print("Scrape: could not open url ", url)
        return bs

    # Step though all summery pages (Next, Pagination) and from each summary page get all the link refering to the articles
    def get_pagination_links(self, sub_site):
        include_url = urlparse(sub_site).scheme + "://" + urlparse(sub_site).netloc
        links = set()
        url = sub_site
        page_nr = 0
        page_size = 10
        link_count = 1
        links.add(sub_site)
        return links

    # get all the links that point within this site
    def get_internal_links(self, url, bs):
        include_url = urlparse(url).scheme + "://" + urlparse(url).netloc
        links = set()
        link_count = 0
        for link_tag in bs.findAll("a", href=re.compile("^(/|.*" + include_url + ")")) and link_count < self.nrpages:
            if link_tag.attrs['href'] is not None:
                if link_tag.attrs['href'] not in links:
                    if link_tag.attrs['href'].startswith('/'):
                        link = include_url + link_tag.attrs['href']
                    else:
                        link = link_tag.attrs['href']
                    links.add(link)
                    link_count = link_count + 1
        return links

    # get all the links that point outside this site
    def get_external_links(self, url, bs):
        include_url = urlparse(url).scheme + "://" + urlparse(url).netloc
        links = set()
        for link_tag in bs.findAll("a", href=re.compile("^(/|.*" + include_url + ")")):
            if link_tag.attrs['href'] is not None:
                if link_tag.attrs['href'] not in links:
                    if link_tag.attrs['href'].startswith('/'):
                        links.append(include_url + link_tag.attrs['href'])
                    else:
                        link_tag.append(link.attrs['href'])
        return links

    # for this page (url) scrape its context and map this to the elasticsearch record (pagemap)
    def scrape_page_map(self, sub_site, url, bs):
        id = url
        site_url = urlparse(url).netloc.split('.')[1]
        sub_site_url = urlparse(url).path.split('/')
        sub_site_name = '-'.join(sub_site[1:-1])
        if sub_site_name == '':
            sub_site_name = 'Home'
        pagemap = models.PageMap()

        pagemap.page_id = id
        pagemap.site = self.site
        pagemap.sub_site = sub_site
        pagemap.url = url
        pagemap.section = ''

        # get posted date
        try:
            pagemap.posted_date = datetime.today()
        except:
            pass

        # get page
        try:
            pagemap.page = bs.get_text()
        except:
            pass

        # get title
        try:
            if bs.title != None:
                pagemap.title = bs.title.text
            else:
                pagemap.title = ''
        except:
            pass

        data = elastic.convert_for_bulk(pagemap, 'update')
        return data