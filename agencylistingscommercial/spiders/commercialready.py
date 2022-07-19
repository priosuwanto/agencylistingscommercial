import scrapy
import json
from datetime import date
from ..items import AgentsItem
from ..items import AgenciesItem



class CommercialreadySpider(scrapy.Spider):
    name = 'commercialready'
    allowed_domains = ['commercialready.com.au']
    start_urls = []


    start_urls.append("https://www.commercialready.com.au/for-sale/qld/real-estate-and-property?locations=queensland")#&opt%5Bsorts%5D=newest

    start_urls.append("https://www.commercialready.com.au/sold/qld/real-estate-and-property?locations=queensland")


    state_list = ["QLD","VIC","NT","TAS","NSW","SA","WA","ACT"]


    def parse(self, response):


        for agent in response.css("div.list-agent-logo a"):

            agent_url = response.urljoin(agent.css("::attr(href)").extract_first(default=""))

            agency_url = agent_url.split("/agent/")[0]

            yield response.follow(url=agency_url, callback=self.parse_agency)

            #return


        next_link = response.css("li.next a::attr(href)").extract_first(default="")
        
        if next_link!="":
            yield response.follow(url=next_link, callback=self.parse)





    def parse_agency(self, response):



        agency_item = AgenciesItem()


        agency_item['name'] = response.css("h2.agency-title::text").extract_first(default="")


        if not agency_item['name']:
            return

        agency_item['url'] = ""#response.url



        for li in response.css("ul.details-list li"):


            img_src = li.css("img.img-responsive::attr(src)").extract_first(default="")


            if "web-icon.svg" in img_src:

                agency_item['url'] = li.css("div.value a::text").extract_first(default="")





            if "//" not in agency_item['url']:
                agency_item['url'] = ""
        


        agency_item['agent_count'] = len(response.css("div.agent-name").getall())


        qld_count = 0
        vic_count = 0
        nt_count = 0
        tas_count = 0
        nsw_count = 0
        sa_count = 0
        wa_count = 0
        act_count = 0

        markets = []
        brisbane_market = 0
        for addr in response.css("h4.address"):

            address = addr.css("::text").extract_first(default="").split(", ")

            market = address[0] +", "+address[1].replace(" ",", ")

            if market not in markets:
                markets.append(market)

                if "qld" in market.lower():
                    brisbane_market = brisbane_market+1
                    qld_count = qld_count+1
                elif "vic" in market.lower():
                    vic_count = vic_count+1
                elif "nt" in market.lower():
                    nt_count = nt_count+1
                elif "tas" in market.lower():
                    tas_count = tas_count+1
                elif "nsw" in market.lower():
                    nsw_count = nsw_count+1
                elif "sa" in market.lower():
                    sa_count = sa_count+1
                elif "wa" in market.lower():
                    wa_count = wa_count+1
                elif "act" in market.lower():
                    act_count = act_count+1




            #print("---"+market)



        agency_item['market_count'] = len(markets)


        agency_item['brisbane_council_markets'] = brisbane_market

        try:
            agency_item['brisbane_council_markets_percent'] = round(brisbane_market/len(markets)*100,2)
        except:
            agency_item['brisbane_council_markets_percent'] = 0

        agency_item['markets'] = " , ".join(markets)


        agency_address = response.css("h5.agency-address-title::text").extract_first(default="").strip().split(" ")

        try:
            state = agency_address[-2].replace(",","")
        except:
            state = ""

        if state in self.state_list:

            agency_item['state'] = state

        else:


            if qld_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "QLD"
            elif vic_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "VIC"
            elif nt_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "NT"
            elif tas_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "TAS"
            elif nsw_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "NSW"
            elif sa_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "SA"
            elif wa_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "WA"
            elif act_count == max(qld_count,vic_count,nt_count,tas_count,nsw_count,sa_count,wa_count,act_count):
                agency_item['state'] = "ACT"




        agency_item['source'] = "commercialready.com.au"

        
        agency_item['sale_type'] = "Sale"



        yield agency_item

