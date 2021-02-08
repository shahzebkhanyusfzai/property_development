import scrapy
from selenium import webdriver
from scrapy import Selector
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
driver = webdriver.Chrome(ChromeDriverManager().install())
from scrapy.crawler import CrawlerProcess
from fake_useragent import UserAgent
ua = UserAgent()
import os 
import requests
from collections import OrderedDict
from datetime import date
from selenium.webdriver.common.keys import Keys
import re
import urllib3

class property_spider(scrapy.Spider):
    name = 'Faircity'
    allowed_domains = ['www.google.com']
    start_urls = ['https://www.google.com']
    ua = UserAgent()
    urllib3.disable_warnings()

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'monthly_data.csv',
        'FEED_EXPORT_ENCODING':'utf-8'
    }
    
    def __init__(self):
        self.options = ChromeOptions()
        self.options.add_argument("--disable-blink-features")
        self.options.add_argument("start-maximized")
        self.options.add_argument('--disable-gpu')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--incognito')
        self.options.add_argument("--disable-blink-features=AutomationControlled")
        self.options.add_argument('ignore-certificate-errors')
        self.options.add_argument("--use-fake-ui-for-media-stream")
        self.options.add_argument("--allow-running-insecure-content")
        self.options.add_argument(
            f'--user-agent={self.ua.chrome}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(),chrome_options=self.options)
        


    def parse(self,response):
        self.driver.get("https://propertydevelopment.ssc.nsw.gov.au/T1PRPROD/WebApps/eproperty/P1/eTrack/eTrackApplicationSearchResults.aspx?Field=S&Period=LM&Group=DA&SearchFunction=SSC.P1.ETR.SEARCH.DA&r=SSC.P1.WEBGUEST&f=SSC.ETR.SRCH.SLM.DA&ResultsFunction=SSC.P1.ETR.RESULT.DA")
        driver.implicitly_wait(10) 
        l=[]
        
        p=1 
        
        while True:
            
            resp = Selector(text=self.driver.page_source) 
            time.sleep(1)   
            links = resp.xpath('(//a)[position()>52 and position()<68]/text()').getall()   
            
            # Getting all the links of DA20/xx
            for a in links: 
                
                a = a.replace('/','%2f') 
                a = 'https://propertydevelopment.ssc.nsw.gov.au/T1PRProd/WebApps/eProperty/P1/eTrack/eTrackApplicationDetails.aspx?r=SSC.P1.WEBGUEST&f=$P1.ETR.APPDET.VIW&ApplicationId='+a
                l.append(a)
                
                

            # Pagination

            try:
                p=p+1
                time.sleep(2) 
                self.driver.find_element_by_xpath('(//table[@border="0"]/tbody/tr/td)['+str(int(p))+']').click()     
                      
            except :
                self.driver.get(l[1])
                time.sleep(2)
                
                break
        time.sleep(2)  
        for link in l:
            
            
            self.driver.get(link)
            
            time.sleep(2)
            resp1 = Selector(text=self.driver.page_source)
            application_ID = resp1.xpath('(((//tbody)[1]/tr)[1]/td)[2]/text()').get()
            description = resp1.xpath ('(((//tbody)[1]/tr)[2]/td)[2]/text()').get()
            Group = resp1.xpath('(((//tbody)[1]/tr)[3]/td)[2]/text()').get()
            Category = resp1.xpath('(((//tbody)[1]/tr)[4]/td)[2]/text()').get()
            Sub_category = resp1.xpath('(((//tbody)[1]/tr)[5]/td)[2]/text()').get().strip()
            Lodgement_Date = resp1.xpath('(((//tbody)[1]/tr)[6]/td)[2]/text()').get()
            Estimated_cost = resp1.xpath ('(((//tbody)[1]/tr)[7]/td)[2]/text()').get()
            Contact  = resp1.xpath('(((//tbody)[2]/tr)[1]/td)[2]/text()').get()
            Notification_Start_Date = resp1.xpath('(((//tbody)[2]/tr)[3]/td)[2]/text()').get().strip()
            Notification_End_Date = resp1.xpath ('(((//tbody)[2]/tr)[4]/td)[2]/text()').get().strip()   
            Review_date = resp1.xpath ('(((//tbody)[2]/tr)[5]/td)[2]/text()').get().strip()
            Address = resp1.xpath ('(((//tbody)[3]/tr[@class="normalRow" or "alternateRow"])[position()>1 and position()<7]/td)[position() mod 2 !=0]/text()').getall()
            Land_description  = resp1.xpath('(((//tbody)[3]/tr[@class="normalRow" or "alternateRow"])[position()>1 and position()<7]/td)[position() mod 2 =0]/text()').getall()
            Name = resp1.xpath('((//tbody)[4]/tr[@class="normalRow"]/td/text())[1]').get()
            Association = resp1.xpath ('((//tbody)[4]/tr[@class="normalRow"]/td/text())[2]').get()
            Determined_date = resp1.xpath ('((//tbody)[5]/tr[@class="normalRow"]/td/text())[2]').get().strip()
            Decision  = resp1.xpath('(((//tbody)[5]/tr)[2]/td)[2]/text()').get()
            Land_env = resp1.xpath('((//tbody)[5]/tr[@class="normalRow"]/td/text())[4]').get().strip()
            
            time.sleep(2)


            self.driver.find_element_by_xpath('(//tbody)[7]/tr[@class="normalRow"]').click()

            driver.implicitly_wait(20)
            
            resp2 = Selector(text=self.driver.page_source)
            
            pdf_name = resp2.xpath('//td/a/text()').getall()
            pdf_links = resp2.xpath('//td/a/@href').getall()
            
           
            
            
            pdf = zip(pdf_name, pdf_links)
            for n,s in pdf:
                
                s = s.strip()
                s = re.sub(r"\s+", '%20', s)
                n = n.replace(' ','-')
                os.chdir(r'C:\Users\DELL\OneDrive\pdf\property_development')
                application_ID = application_ID.replace('/','-')
                if not os.path.exists(application_ID):
                    os.mkdir(application_ID)
                os.chdir(f'C:\\Users\\DELL\\OneDrive\\pdf\\property_development\\{application_ID}')
                r = requests.get(s, verify = False)
                open(n+'.pdf','wb').write(r.content)
                 
            

            yield {
            'Application ID': application_ID,
            'Description': description,
            'Group': Group,
            'Category': Category,
            'Sub-Category': Sub_category,
            'Lodgement date ': Lodgement_Date,
            'Estimated cost':Estimated_cost,
            'Contact': Contact,
            'Notification start date': Notification_Start_Date,
            'Notification end date':Notification_End_Date,
            'Review date':Review_date,
            'Address': Address,
            'Land Description': Land_description,
            'Name':Name,
            'Association': Association,
            'Determined date':Determined_date,
            'Decision':Decision,
            'Land & env':Land_env
            }
           
        

process = CrawlerProcess()
process.crawl(property_spider)
process.start()


driver.quit()