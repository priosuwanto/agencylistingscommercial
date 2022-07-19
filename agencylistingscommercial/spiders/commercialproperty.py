import scrapy
import json
from datetime import date
from ..items import AgentsItem
from ..items import AgenciesItem



class CommercialpropertySpider(scrapy.Spider):
    name = 'commercialproperty'
    allowed_domains = ['commercialproperty.com.au']
    start_urls = ['https://commercialproperty.com.au/offices?page=1']

    def parse(self, response):



        for card in response.css("div.office.col-md-4"):


            agency_url = card.css("div.card.cursor-pointer::attr(data-url)").extract_first(default="")


            #print("---"+agency_url)
            yield response.follow(url=next_link, callback=self.parse)
            return



        # next_link = response.css("a.page-link.next::attr(href)").extract_first(default="")
        # if next_link:
        #     yield response.follow(url=next_link, callback=self.parse)





    def parse_agency(self, response):



        agency_item = AgenciesItem()



        agency_item['name'] = response.css("div.office-summary h2::text").extract_first(default="")


        