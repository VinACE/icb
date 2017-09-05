
"""
#  Main Class to conduct the batch processing of  website Crawl
# this Program calls all  websites crawl routine
# Feature thought is to do Crawl in Parallel program
# Either with multi threaded  or parallel program
# Also Need to consider the performance of ESearch when doing the parallel program
"""

from helper.helpervariable import *
from batch.icrawl_cosmetics import  CosmeticsCrawler
from batch.icrawl_apf import AFPCrawler



if __name__ == '__main__':

   hv = HelperVariable()

   # scrape_choices = (('market', 'Market'), ('business', 'Business'), ('product', 'Product'), ('events', 'Events'),
   #                 ('publications', 'Publications'), ('blog', 'Blog'))

   cosmetics_batch_crawl= CosmeticsCrawler()
   cosmetics_batch_crawl.crawl_cosmetic(hv.COS_SCRAPE_CHOICES, nrpages=1)
