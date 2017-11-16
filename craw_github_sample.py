# -*- coding: utf-8 -*-
import os
import re
import scrapy
import sys
from scrapy.spiders import CrawlSpider, Spider
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from scrapy.selector import Selector
import time
from CrawlMacApp.items import CrawlmacappItem
import csv
import urllib2
from lxml import etree

class SampleGithub(scrapy.Spider):
    name = 'sample_github_spider'
    sou_path = os.getcwd()
    base_url = "https://github.com"
    # allowed_domains = ['python.org']
    # start_urls = ['http://www.sina.com.cn/']

    def start_requests(self):
        d_f = 'D:\\SampleCrawler\\CrawlMacApp\\spiders\\firstlayer_gazers.csv'
        reader = csv.reader(open(d_f, 'rU'), dialect='excel')
        for each in reader:
            each_gazer = each[0]
            each_gazer_repositories=each_gazer+"?tab=repositories"
            #print each_gazer_repositories
            yield scrapy.Request(url=each_gazer_repositories, callback=self.parse)


    def parse(self, response):
        #print response.url
        #进入存储CSV目录
        #D:\SampleCrawler\CrawlMacApp\spiders\Gazers_Repositories\github.com_KingsWoo.txt
        #os.chdir("./CrawlMacApp/spiders/Gazers_Repositories")

        gazer_repos_name=response.url.split('?')[0].split('/')[-1]
        gazer_repo_file="github.com_"+gazer_repos_name+'.txt'
        #print(gazer_repo_file)
        #每个 gazer 的所有项目仓
        res=response.xpath('//*[@id="user-repositories-list"]/ul/li/div[1]/h3/a/@href').extract()

        for each_repo_file in res:
            each_repo_file_url=self.base_url+each_repo_file
            yield scrapy.Request(url=each_repo_file_url,callback=self.pre_each_repo,meta={"sav_file":gazer_repo_file})
    #处理每个仓中的文件
    def pre_each_repo(self,response):
        #print(response.url)
        #获取第一层文件目录
        firstlay_files = response.xpath('//tbody/tr[contains(@class,"js-navigation-item")]/td[contains(@class,"content")]/span/a/@href').extract()
        sav_file=response.meta["sav_file"]
        for each_firstlay_file in firstlay_files:
            each_firstlay_file_url=self.base_url+each_firstlay_file
            #print(each_firstlay_file_url)

            yield scrapy.Request(url=each_firstlay_file_url,callback=self.pre_fromsecondlay_file,meta={"sav_file":sav_file})

    # 处理从第二层开始的文件
    def solv_secondlay_response(self, url):
        yield scrapy.Request(url=url, callback=self.pre_fromsecondlay_file)

    def pre_fromsecondlay_file(self,response):
        #print(response.url)
        sav_file=response.meta["sav_file"]
        #print(sav_file)
        #sav_file=open("0000.csv",'a+')
        try:
            t_f=open(sav_file,'a+')
            secondlay_files=response.xpath('//tr[@class="js-navigation-item"]/td[2]/span/a/@href').extract()
            if len(secondlay_files)>0:
                for each in secondlay_files:
                    each_url=self.base_url+each
                    # yield scrapy.Request(url=each_url,callback=self.pre_fromsecondlay_file)
                    header = {
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/62.0.3202.75 Chrome/62.0.3202.75 Safari/537.36"
                    }

                    def presgh(sou_url):

                        request = urllib2.Request(url=sou_url, headers=header)
                        response = urllib2.urlopen(request).read()
                        content = etree.HTML(response)
                        # 获取一层 URL 进一步提取的下层链接
                        res = content.xpath('//tr[@class="js-navigation-item"]/td[2]/span/a/@href')
                        if len(res) > 0:
                            for each_elem in res:

                                presgh(each_url )
                        else:
                            t_f.write(sou_url + "\n")


                    self.solv_secondlay_response(each_url)

            else:
                print(response.url)
                #sav_file.write(response.url)
                #s_f = csv.writer(t_f,dialect='excel')
                t_f.write(response.url+'\n')
            #os.chdir(self.sou_path)
        except Exception,e:
            print(e.message)











