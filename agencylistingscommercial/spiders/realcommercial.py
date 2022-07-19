import scrapy
import json
from datetime import date
from ..items import AgentsItem
from ..items import AgenciesItem


class RealcommercialSpider(scrapy.Spider):
    name = 'realcommercial'
    allowed_domains = ['realcommercial.com.au','customer-profile-experience-api.resi-agent-prod.realestate.com.au']
    start_urls = ['https://www.realcommercial.com.au/find-agent/in-queensland+-+region%2c+qld/list-1?channel=for-sale','https://www.realcommercial.com.au/find-agent/in-queensland+-+region%2c+qld/list-1?channel=for-lease']
    
    custom_settings = {'HTTPERROR_ALLOW_ALL': True}


    headers = { "content-type": "application/json",
                'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'  }


    body = '{"query":"query getCommercialAgencyListings($agencyId: String!, $channel: String!, $page: Int, $pageSize: Int, $locations: [String], $propertyTypes: [String]) {\n  commercialAgencyListings(\n    agencyId: $agencyId\n    channel: $channel\n    page: $page\n    pageSize: $pageSize\n    locations: $locations\n    propertyTypes: $propertyTypes\n  ) {\n    listings {\n      id\n      price\n      listingStatus\n      address {\n        shortAddress\n        suburb\n        state\n        postcode\n        __typename\n      }\n      propertySizes {\n        preferred {\n          size {\n            displayValue\n            __typename\n          }\n          sizeType\n          __typename\n        }\n        __typename\n      }\n      listers {\n        id\n        name\n        photo {\n          templatedUrl\n          __typename\n        }\n        __typename\n      }\n      listingCompany {\n        id\n        __typename\n      }\n      propertyType\n      productDepth\n      media {\n        mainImage\n        images\n        __typename\n      }\n      _links {\n        canonical\n        __typename\n      }\n      ... on SoldListing {\n        listingStatus\n        __typename\n      }\n      ... on BuyListing {\n        listingStatus\n        __typename\n      }\n      ... on RentListing {\n        listingStatus\n        __typename\n      }\n      __typename\n    }\n    mapClusters {\n      count\n      latitude\n      longitude\n      listingIds\n      longitude\n      __typename\n    }\n    totalResultsCount\n    pagination {\n      page\n      pageSize\n      maxPageNumberAvailable\n      __typename\n    }\n    __typename\n  }\n}\n","operationName":"getCommercialAgencyListings","variables":{"agencyId":"---AGENCY-ID---","channel":"---CHANNEL---","page":---PAGE---,"pageSize":20}}'

    body =  body.replace('\n','')

    graphql_url = 'https://customer-profile-experience-api.resi-agent-prod.realestate.com.au/graphql'

    def parse(self, response):


        temp = response.text.split('"results":[{"')[1].split("</script>")[0].split('id":"')


        for item in temp:

            item_id = item.split('"')[0]


            if len(item_id)>10 or len(item_id)<3:
                continue

            item_name = item.split('"name":"')[1].split('"')[0].replace(" ","XXXXX")

            url = ''.join(ch for ch in item_name if ch.isalnum()).replace("XXXXX","-").lower() +"-"+item_id

            agency_url = "https://www.realcommercial.com.au/agency/"+url.replace("--","-").replace("--","-")



            yield response.follow(url=agency_url, callback=self.parse_agency)




        next_link = response.css("li.pagination-button.pagination-next a.active::attr(href)").extract_first(default="")

        if next_link:
            yield response.follow(url=next_link, callback=self.parse)



    def parse_agency(self, response):



        agency_item = AgenciesItem()


        agency_item['name'] = response.css("h1::text").extract_first(default="")


        if not agency_item['name']:
            return



        try:
            agency_item['url'] = response.text.split('"agencyUrl":"')[1].split('"')[0]
        except:
            agency_item['url'] = ""


        try:
            agency_item['agent_count'] = response.text.split('Meet the team')[1].split('</div>')[0].split('>Showing ')[1].split(' team member')[0]

            if " of " in agency_item['agent_count']:
                agency_item['agent_count'] = agency_item['agent_count'].split(" of ")[1]

        except:
            agency_item['agent_count'] = 0



        agency_item['market_count'] = 0
        agency_item['brisbane_council_markets'] = 0
        agency_item['source'] = "realcommercial.com.au"
        
        try:
            agency_item['state'] = response.css("p.Text__Typography-sc-vzn7fr-0.cDunee.sc-puvyvd-1.kiYA::text").extract_first(default="").split(" ")[-2]
        except:
            agency_item['state'] = "QLD"


        channel_left = []
        active_channel  = response.text.split('"activeChannels":["')[1].split('"]')[0]

        temp = active_channel.split('","')

        for cn in temp:

            channel_left.append(cn)


        #check listing

        agency_item['sale_type'] = ""

        if "SOLD" in channel_left or "BUY" in channel_left:

            agency_item['sale_type'] = "Sale"
        

        if "LEASED" in channel_left or "RENT" in channel_left:


            if agency_item['sale_type'] == "Sale":
                agency_item['sale_type'] = "Sale/"

            agency_item['sale_type'] = agency_item['sale_type'] + "Lease"
        

        

        agency_id = response.url.split('-')[-1]

        channel = channel_left.pop(0)

        page=1

        first_body = self.body.replace('---AGENCY-ID---',agency_id).replace('---CHANNEL---',channel).replace('---PAGE---',str(page))
        
        markets = []
        yield scrapy.Request(url=self.graphql_url,
                        method='POST',
                        headers=self.headers,
                        body=first_body,
                        dont_filter=True,
                        callback=self.parse_property,
                        meta={"page":"1","channel":channel,"channel_left":channel_left,"agency_id":agency_id,"agency_item":agency_item,"markets":markets})




    def parse_property(self, response):

        page = int(response.meta.get("page"))
        agency_item = response.meta.get("agency_item")
        channel = response.meta.get("channel")
        channel_left = response.meta.get("channel_left")

        agency_id = response.meta.get("agency_id")
        markets = response.meta.get("markets")


        jsn = json.loads(response.text)

        listings = jsn['data']['commercialAgencyListings']['listings']
        for item in listings:


            market = item['address']['suburb']+", "+item['address']['state']+", "+item['address']['postcode']


            if market not in markets:
                agency_item['market_count'] = agency_item['market_count'] + 1
                markets.append(market)

                if " qld," in market.lower():
                    agency_item['brisbane_council_markets'] = agency_item['brisbane_council_markets'] +1



        submit=False
        if len(listings)>=20:
            next_page = page+1
            submit = True

        elif len(channel_left)>0:

            next_page = 1
            channel = channel_left.pop(0)
            submit=True


        else:

            try:
                agency_item['brisbane_council_markets_percent'] = round(agency_item['brisbane_council_markets']/len(markets)*100,2)
            except:
                agency_item['brisbane_council_markets_percent'] = 0


            agency_item['markets'] = " , ".join(markets)

            yield agency_item



        if submit:
            next_body = self.body.replace('---AGENCY-ID---',agency_id).replace('---CHANNEL---',channel).replace('---PAGE---',str(next_page))
            yield scrapy.Request(url=self.graphql_url,
                method='POST',
                headers=self.headers,
                body=next_body,
                dont_filter=True,
                callback=self.parse_property,
                meta={"page":str(next_page),"channel":channel,"channel_left":channel_left,"agency_id":agency_id,"agency_item":agency_item,"markets":markets})
