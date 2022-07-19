# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy



class AgenciesItem(scrapy.Item):

    name = scrapy.Field()
    url = scrapy.Field()
    agent_count = scrapy.Field()
    market_count = scrapy.Field()
    brisbane_council_markets = scrapy.Field()
    brisbane_council_markets_percent = scrapy.Field()
    state = scrapy.Field()
    markets = scrapy.Field()
    source = scrapy.Field()
    sale_type = scrapy.Field()
    

class AgentsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    
    url = scrapy.Field()
    first_name = scrapy.Field()
    last_name = scrapy.Field()
    mobile_number = scrapy.Field()
    email = scrapy.Field()
    agency_url = scrapy.Field()


    