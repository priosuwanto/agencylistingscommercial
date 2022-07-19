import scrapy
import json
from datetime import date
from ..items import AgentsItem
from ..items import AgenciesItem


class CommercialrealestateSpider(scrapy.Spider):
    name = 'commercialrealestate'
    allowed_domains = ['commercialrealestate.com.au','www.commercialrealestate.com.au']
    start_urls = ['https://www.commercialrealestate.com.au/findanagent/qld/']



    listing_url = 'https://www.commercialrealestate.com.au/bf/api/gqlb?operationName=agencyListingsQuery&variables=%7B%22agencyIds%22%3A%5B---AGENCY_ID---%5D%2C%22'
    listing_url = listing_url + 'searchType%22%3A---SEARCH_TYPE---%2C%22pageNo%22%3A---PAGE_NO---%2C%22pageSize%22%3A6%7D&'
    listing_url = listing_url + 'extensions=%7B%22persistedQuery%22%3A%7B%22version%22%3A1%2C%22sha256Hash%22%3A%22130fe0b691f7ee6bfb4c4f86ca51cdd0efdace7401b2c6266930f5250eb91a7f%22%7D%7D'



    def parse(self, response):

        #a=0
        for item in response.css("div.css-17u87e8"):

            #a=a+1
            agency_url = response.urljoin(item.css("a.css-1bmulkz::attr(href)").extract_first(default=""))


            #if a<2:
            #    continue
            #print("---"+agency_url)

            yield response.follow(url=agency_url, callback=self.parse_agency)
            #return


        nav_link = response.css("a.css-7ju1xm::attr(href)").getall()#extract_last(default="")
        next_link = nav_link[-1]

        if next_link:
            yield response.follow(url=next_link, callback=self.parse)





    def parse_agency(self, response):

        agency_item = AgenciesItem()

        agency_item['name'] = response.css("h1.css-ittoh5::text").extract_first(default="")


        if not agency_item['name']:
            return


        agency_item['url'] = response.css("a.touchable.css-1gyr8oz::attr(href)").extract_first(default="")


        agentnames = response.text.split('agentName":"')


        agency_item['agent_count'] = len(agentnames)-1


        agency_item['source'] = "commercialrealestate.com.au"
        

        sold = response.text.split('"numberSold":')[1].split(',')[0]
        leased = response.text.split('"numberLeased":')[1].split(',')[0]
        rent = response.text.split('"numberForRent":')[1].split(',')[0]
        sale = response.text.split('"numberForSale":')[1].split(',')[0]
        business = response.text.split('"numberBusiness":')[1].split(',')[0]


        agency_item['sale_type'] = ""

        if int(sold)>0 or int(sale)>0:

            agency_item['sale_type'] = "Sale"
        

        if int(rent)>0 or int(leased)>0:


            if agency_item['sale_type'] == "Sale":
                agency_item['sale_type'] = "Sale/"

            agency_item['sale_type'] = agency_item['sale_type'] + "Lease"
        

        agency_item['state'] = response.text.split('"addressRegion":"')[1].split('"')[0]


        markets=[]
        agency_item['market_count'] = 0
        agency_item['brisbane_council_markets'] = 0

        agency_id = response.url.split("-")[-1]
        
        #---SEARCH_TYPE--- 
        #6 //for sale
        #7 //for lease//rent
        #8 //sold
        #9 //leased
        #0 //bussiness

        search_type_left = []
        if int(business)>0:
            search_type_left.append(0)
        if int(sale)>0:
            search_type_left.append(6)
        if int(rent)>0:
            search_type_left.append(7)
        if int(sold)>0:
            search_type_left.append(8)
        if int(leased)>0:
            search_type_left.append(9)


        #search_type_left = [6,7,8,9]


        if len(search_type_left)>0:
            search_type = search_type_left.pop(0)
            page=1
            property_listing_url = self.listing_url.replace("---AGENCY_ID---",str(agency_id)).replace("---SEARCH_TYPE---",str(search_type)).replace("---PAGE_NO---",str(page)) 

            yield response.follow(url=property_listing_url, callback=self.parse_property,meta={"agency_id":agency_id,"page":page,"search_type":search_type,"search_type_left":search_type_left,"agency_item":agency_item,"markets":markets})

        else:


            agency_item['brisbane_council_markets_percent'] = 0


            agency_item['markets'] = ""


            yield agency_item
        #print(agency_item)





    def parse_property(self, response):

        agency_id = response.meta.get("agency_id")
        page = int(response.meta.get("page"))
        agency_item = response.meta.get("agency_item")
        search_type_left = response.meta.get("search_type_left")
        search_type = response.meta.get("search_type")
        markets = response.meta.get("markets")


        jsn = json.loads(response.text)

        try:
            listings = jsn['data']['searchListings']['pagedSearchResults']
        except:
            yield response.follow(url=response.url, callback=self.parse_property,dont_filter=True,meta={"agency_id":agency_id,"page":page,"search_type":search_type,"search_type_left":search_type_left,"agency_item":agency_item,"markets":markets})
            return


        # print("----------------------------search_type="+str(search_type))
        # print("----------------------------page="+str(page))
        # print("-----------------------LEN LISTINGS-----"+str(len(listings)))
        # print("-----------------------LEN search_type_left-----"+str(len(search_type_left)))

        # print(agency_item)



        for item in listings:

            market = item['suburb']+", "+item['state']+", "+item['postcode']

            if market not in markets:
                agency_item['market_count'] = agency_item['market_count'] + 1
                markets.append(market)

                if " qld," in market.lower():
                    agency_item['brisbane_council_markets'] = agency_item['brisbane_council_markets'] +1


        if len(listings)>=6:
            next_page = page+1

            property_listing_url = self.listing_url.replace("---AGENCY_ID---",str(agency_id)).replace("---SEARCH_TYPE---",str(search_type)).replace("---PAGE_NO---",str(next_page)) 

            yield response.follow(url=property_listing_url, callback=self.parse_property,meta={"agency_id":agency_id,"page":next_page,"search_type":search_type,"search_type_left":search_type_left,"agency_item":agency_item,"markets":markets})


        elif len(search_type_left)>0:

            next_page = 1
            search_type = search_type_left.pop(0)
        
            property_listing_url = self.listing_url.replace("---AGENCY_ID---",str(agency_id)).replace("---SEARCH_TYPE---",str(search_type)).replace("---PAGE_NO---",str(next_page)) 

            yield response.follow(url=property_listing_url, callback=self.parse_property,meta={"agency_id":agency_id,"page":next_page,"search_type":search_type,"search_type_left":search_type_left,"agency_item":agency_item,"markets":markets})


        else:

            try:
                agency_item['brisbane_council_markets_percent'] = round(agency_item['brisbane_council_markets']/len(markets)*100,2)
            except:
                agency_item['brisbane_council_markets_percent'] = 0


            agency_item['markets'] = " , ".join(markets)

            yield agency_item