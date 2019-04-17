#coding:utf8
'''
Created on 2018年8月8日

@author: Administrator
'''
import spider.download_ws_titleSearch
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import operator
from selenium import webdriver

def search_title(driver,title):
    #根据文章的题目在web of science中搜索，如果搜索到返回True，否则返回false
    for i in range(1,5):
        driver.find_element_by_xpath('//*[@id="searchrow1"]/td[2]/span/span[1]/span/span[2]/b').click()
        text=driver.find_element_by_xpath('/html/body/span[25]/span/span[2]/ul').find_element_by_css_selector("li:nth-of-type(2)").click()
    input=driver.find_element_by_xpath('//*[@id="value(input1)"]')
    input.send_keys(title)
    search_button=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button').click()
    soup=BeautifulSoup(driver.page_source,"html5lib")
    search_result=soup.find_all(string="检索后没有发现记录。")
    if  search_result:
        return False;
    else:
        return True;

def search_doi(driver,doi):
    #根据DOI爬取文章，搜索到结果返回True，否则返回False
    for i in range(1,5):
        driver.find_element_by_xpath('//*[@id="searchrow1"]/td[2]/span/span[1]/span/span[2]/b').click()
        text=driver.find_element_by_xpath('/html/body/span[25]/span/span[2]/ul').find_element_by_css_selector("li:nth-of-type(8)").click()
    input=driver.find_element_by_xpath('//*[@id="value(input1)"]')
    input.send_keys(doi)
    search_button=driver.find_element_by_xpath('//*[@id="searchCell1"]/span[1]/button').click()
    soup=BeautifulSoup(driver.page_source,"html5lib")
    search_result=soup.find_all(string="检索后没有发现记录。")
    if  search_result:
        return False;
    else:
        return True;
def download_ws_firstPaper(driver,dirname,paper_id):#通过selenium模拟点击的形式，从web of science下载论文
 
    #driver.find_element_by_xpath('//*[@id="SelectPageChkId"]').click()#模拟点击选择页面的checkbox
    driver.find_element_by_xpath('//*[@id="RECORD_1"]/div[3]/div[1]/div/a').click()#点击搜索结果第一个文章的titile
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div[26]/div/div/div/div[4]/span/span/span[1]/span/span[2]').click();
    #点击上方选择保存格式
    driver.find_element_by_xpath('//*[@id="select2-saveToMenu-results"]/li[4]').click();
    #点击选择  保存为其它文件格式
    driver.find_element_by_xpath('//*[@id="select2-saveToMenu-container"]')
   
    driver.find_element_by_xpath('//*[@id="ui-id-5"]/form/div[4]/span/button').click()
    driver.implicitly_wait(5)
def init_chromeDriver(dirname):
    option=webdriver.ChromeOptions()
    #argument1='--user-data-dir='+dirname
    #chrome_option.add_argument(argument1)
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory':dirname}
    option.add_experimental_option('prefs',prefs)  
    driver=webdriver.Chrome(chrome_options=option)
    url="http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product=UA&search_mode=GeneralSearch&SID=5DC3F1w3pyIDNxvfdmI&preferencesSaved="
    driver.get(url)
    wait_result = WebDriverWait(driver, timeout=1000, poll_frequency=2,  ignored_exceptions=None).until(
        EC.visibility_of_element_located((By.XPATH,'/html/body/div[8]/div/ul/li[1]/a')))
    return driver;
def spider_ws_doiORtitle(title,doi,dirname,ID):#根据文章的DOI或者title在web of science中下载对应论文
    
        
   # dirname = 'F:\\test' 
    
    driver=init_chromeDriver(dirname)
   # doi='10.1109/SOSE.2008.9'
    search=search_doi(driver,doi)
    print(search)
    print(operator.eq(search,True))
    if(operator.eq(search,True)):
        download_ws_firstPaper(driver,dirname,'0')
        driver.close()
    else:
        driver.close()
        driver=init_chromeDriver(dirname)
        search=search_title(driver,title)
        if(operator.eq(search,True)):
            file_name="page"+str(ID)
            search_url=driver.current_url;
            print(search_url)
            print(title)
            print(dirname)
            print(file_name)
            spider.download_ws_titleSearch.start_download(search_url, title, dirname,file_name)
            driver.close()
        else: 
            return 0
        
    
    
        
       
