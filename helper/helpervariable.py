from utils.configmanager import ConfigManager
import utils.loggerutils as logger
from datetime import datetime

class HelperVariable(object):

    def __init__(self):

        try:
            self.config_manager = ConfigManager()

        except Exception as ex:
            logger.error('Exception Received while trying to set-up config-manager')

        self.APF_SITE_URL = str(self.config_manager.config_item \
                                            ('APF_CRAWL_SITE', 'APF_SITE_URL'))
        self.APF_SCRAPE_CHOICES = str(self.config_manager.config_item \
                                        ('APF_CRAWL_SITE', 'APF_SCRAPE_CHOICES'))
        self.COS_DESIGN_SITE_URL = str(self.config_manager.config_item \
                                        ('COS_DESIGN_SITE', 'COS_DESIGN_SITE_URL '))
        self.COS_SCRAPE_CHOICES = str(self.config_manager.config_item \
                                        ('COS_DESIGN_SITE', 'COS_SCRAPE_CHOICES'))
        ##############################################################################################







        ###############################################################################################
'''
if __name__ == "__main__":

    h = HelperVariable()
    print(h.APF_SCRAPE_CHOICES)
    print(h.APF_SITE_URL)
    print(h.COS_DESIGN_SITE_URL)
    print(h.COS_SCRAPE_CHOICES)
    print(h.COS_DESIGN_SITE_URL)
'''
