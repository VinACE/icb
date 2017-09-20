"""
#  Main Class to conduct the batch processing of  website Crawl
# this Program calls all  websites crawl routine
# Feature thought is to do Crawl in Parallel program
# Either with multi threaded  or parallel program
# Also Need to consider the performance of ESearch when doing the parallel program
"""

from helper.helpervariable import HelperVariable
from batch.icrawl_cosmetics import  CosmeticsCrawler
from batch.icrawl_apf import AFPCrawler
from batch.icrawl_contagious import  ContagiousCrawler


class InsightBatchCrawl(object):
    def __init__(self):

        self.hv = HelperVariable()

    def start_batch(self):

        # apf_batch_crawl = AFPCrawler(self.hv.APF_SITE_URL, self.hv.NRPAGES)
        # apf_batch_crawl.crawl_apf(self.hv.APF_SCRAPE_CHOICES, self.hv.NRPAGES)
        # cosmetics_batch_crawl = CosmeticsCrawler(self.hv.COS_DESIGN_SITE_URL, self.hv.NRPAGES)
        # cosmetics_batch_crawl.crawl_cosmetic(self.hv.COS_SCRAPE_CHOICES, self.hv.NRPAGES)
        contagious_batch_crawl = ContagiousCrawler(self.hv.CONTAGIOUS_SITE_URL, self.hv.NRPAGES)
        contagious_batch_crawl.crawl_contagious(self.hv.CONTAGIOUS_SCRAPE_CHOICES, self.hv.NRPAGES)


if __name__ == '__main__':
    ibc = InsightBatchCrawl()
    ibc.start_batch()
    # hv = HelperVariable()
    # scrape_choices = (('market', 'Market'), ('business', 'Business'), ('product', 'Product'), ('events', 'Events'),
    #                 ('publications', 'Publications'), ('blog', 'Blog'))

    '''
    print(self.hv.COS_DESIGN_SITE_URL)
    print(self.hv.COS_SCRAPE_CHOICES)

    # batch_crawl = CosmeticsCrawler()

    # scrape_choices = (('market', 'Market'), ('business', 'Business'), ('product', 'Product'), ('events', 'Events'),
    #                 ('publications', 'Publications'), ('blog', 'Blog'))

    # batch_crawl.crawl_cosmetic(scrape_choices, nrpages=1)

    # cosmetics_batch_crawl= CosmeticsCrawler(self.hv.COS_DESIGN_SITE_URL, self.hv.NRPAGES)

    # cosmetics_batch_crawl.crawl_cosmetic(self.hv.COS_SCRAPE_CHOICES, self.hv.NRPAGES)
    #
    

    '''