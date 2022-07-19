# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

import pyodbc
#import datetime
#from datetime import date, timedelta
from twisted.enterprise import adbapi
import re
import os
import platform
import json
import logging
import scrapy
from scrapy import crawler
#from data.states import states
#from data.status_map import status_map
#from data.availability_map import avail_map
#from data.update_trigger_fields import update_fields
from .items import AgentsItem
from .items import AgenciesItem


#from itemadapter import ItemAdapter


class AgencylistingscommercialPipeline:


    
    table_name = ""
        
    connection = ''

    spider = {}

    def __init__(self):
        pass


    async def process_item(self, item, spider):


        
        if isinstance(item, AgenciesItem):
        
            await spider.connection.runQuery(self.insert_query_agency(item))

        elif isinstance(item, AgentsItem):
        
            await spider.connection.runQuery(self.insert_query_agent(item))


        return item



    def insert_query_agency(self, item):
        try:
            query = """BEGIN SET NOCOUNT ON; INSERT INTO AgenciesCommercial VALUES (
                '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}'
            ); SELECT 0; END""".format(
                
                item['name'], item['url'], item['agent_count'], item['market_count'],
                item['brisbane_council_markets'], item['brisbane_council_markets_percent'], item['state'], item['markets'], item['source'], item['sale_type'], 
            )
            
            return query
        except Exception as e:
            logging.error("Error In insert query building")
            #logging.error(item['listing_web_address'])
            logging.error(e, exc_info=True)




    def insert_query_agent(self, item):
        try:
            query = """BEGIN SET NOCOUNT ON; INSERT INTO Agents VALUES (
                '{}', '{}', '{}', '{}', '{}', '{}'
            ); SELECT 0; END""".format(
                
                item['url'], item['first_name'], item['last_name'], item['mobile_number'], item['email'],
                item['agency_url'], 
            )


            return query
        except Exception as e:
            logging.error("Error In insert query building")
            #logging.error(item['listing_web_address'])
            logging.error(e, exc_info=True)




    def open_spider(self, spider):
        #self.start_time = datetime.datetime.now()

        print("Detecting drivers to connect with database...")
        drivers = [item for item in pyodbc.drivers()]
        # print("Driver List: ")
        # print(drivers)

        # print("Selected driver for connection:")
        driver = drivers[-1]
        # print(driver)

        print("Connecting to database...", spider.settings.get('SERVER'), spider.settings.get('DATABASE'), "1433")
        try:
            # Connection string for freetds lib
            self.connection = adbapi.ConnectionPool(
                "pyodbc",
                driver=driver,
                TDS_Version='8.0',
                server=spider.settings.get('SERVER'),
                port=1433,
                database=spider.settings.get('DATABASE'),
                uid=spider.settings.get('USERNAME'),
                pwd=spider.settings.get('PASSWORD'),
                autocommit=True
            )

            spider.connection = self.connection

            # setting spider attaching getSuburbs method to spider to fetch suburbs from database
            self.spider = spider
            #spider.getSuburbs = self.getSuburbs
            #spider.predictItemPropertyType = self.predictItemPropertyType
            self.table_name = spider.settings.get('LISTING_TABLE')

            # Connection string for msodbcsql lib
            # self.dbpool = adbapi.ConnectionPool("pyodbc", "Driver={"+driver+"};Server=tcp:server-remap-io.database.windows.net,1433;Database=db-remap.io;Uid="+username+";Pwd="+password+";Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;", autocommit=True)
            # self.dbpool.runQuery("Select top (1) * from Scraped_data;").addCallback(self.printResult)

            print("Connected to database...")

            # calculating day for full or limited scrapes
            #print("========== > Calculated Day: " + str(self.day_of_week_number) + " ( " + self.day_of_week_name + " ) ")
            spider.stop = False
        except Exception as e:
            print("=================== Connection to database failed ===================")
            print(e)
