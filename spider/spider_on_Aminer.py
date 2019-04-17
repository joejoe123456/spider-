#coding:utf8
'''
Created on 2018年8月3日

@author: Administrator
'''
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.common.by import By
import operator
import selenium
import re
import requests
from itertools import islice
import openpyxl 
from pandas.core.frame import DataFrame
import os 
import time
import string 
import operator
from bs4 import BeautifulSoup
#从http://dx.doi.org/null抽取出DOI信息
def doi_extract(doi_link):
    doi=''
    if doi_link:
        temp=re.match("https?://(?:dx.)?doi.org/(.*)",doi_link.strip())
        temp_doi=temp.group(1)
        doi=temp_doi
    if((operator.eq(doi,'null'))|(operator.eq(doi,'NULL'))):
         doi=''
    return doi;
       
def spider_titleDOI_Aminer(url,name,name_pinyin,result_path):
#根据提供的某个人的url在Aminer中爬取每年发表的文献的名字和DOI
    name_pinyin=process_str(name_pinyin)
    name_pinyin_list=name_pinyin.split()
    name_pinyin_list.reverse()
    name_pinyin_reverse=(' ').join(name_pinyin_list)
   # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
    browser=webdriver.Chrome()
    browser.get(url)
    #print(browser.find_element_by_xpath('//*[@id="demo-pill-nav"]/li[2]/a').text())
    wait_result = WebDriverWait(browser, timeout=2000, poll_frequency=2,  ignored_exceptions=None).until(
     EC.text_to_be_present_in_element((By.XPATH,'//*[@id="demo-pill-nav"]/li[2]/a'), u'Papers'))  
    #点击Papers标签获取作者的论文信息
    #https://api.aminer.cn/api/person/pubs/542aa7eadabfae646d57cc03/range/year/2015/20/20
    
    for i in range(1,10):
        browser.find_element_by_xpath('//*[@id="demo-pill-nav"]/li[2]/a').click()
        wait_result1 = WebDriverWait(browser, timeout=30, poll_frequency=1,  ignored_exceptions=None).until(
            EC.element_to_be_clickable((By.XPATH,'//*[@id="demo-pill-nav"]/li[2]/a'))).click()
        browser.implicitly_wait(15)
    time.sleep(60)
    
      
        
# 而直接操作页面就需要类似于下面的代码等待页面加载完成

    ##确定采集数据的年份数
    soup1=BeautifulSoup(browser.page_source,"html5lib")
    div_but_year=soup1.select("#year > div.btn-toolbar div",limit=1)
   
    ''''
    for item in div_but_year:
    #测试用的代码
     print("*******")
     print(item)
     print("*******")
    '''
    print("len(div_but_year)=",end='')
    print(len(div_but_year))
    button_year=div_but_year[0].find_all("div",attrs={"type":"button","ng-repeat":"y in pubListInfo.years"})
    #"ng-click":"getPubsByYear(y)"
    #根据年份button的div类型选择这些div
    btn_year_num=len(button_year)
    print(btn_year_num)
    number=3
    end_number=number+len(button_year)
    while(number<end_number):
        x_path1='//*[@id="year"]/div[1]/div/div['+str(number)+']'
        print(x_path1)
        wait_result = WebDriverWait(browser, timeout=30, poll_frequency=1,  ignored_exceptions=None).until(
         EC.visibility_of_element_located((By.XPATH,x_path1)))
        year=int(browser.find_element_by_xpath(x_path1).text)
        
        
        #url_js=[url+"/range/year/"+str(year)+"/{}/20".format(i) for i in range(0,60,20)]
        
        #year.click()

        print(year)
        if(year>2001):
            number=number+1
        else:
            author_path=result_path+"\\"+name
            if not os.path.isdir(author_path):
                 os.makedirs(author_path)
            output_path=os.path.join(author_path,str(year)+".xlsx")
            df_temp=DataFrame(columns=['title','doi','publication','cited number in Aminer','author','author_order'])
            wait_result = WebDriverWait(browser, timeout=50, poll_frequency=1,  ignored_exceptions=None).until(
            EC.text_to_be_present_in_element((By.XPATH,x_path1), str(year)))
            for i in range(1,10):
                browser.find_element_by_xpath(x_path1).click()
                wait_result = WebDriverWait(browser, timeout=30, poll_frequency=1,  ignored_exceptions=None).until(
                     EC.element_to_be_clickable((By.XPATH,x_path1))).click()

            wait_result = WebDriverWait(browser, timeout=30, poll_frequency=1,  ignored_exceptions=None).until(
            EC.element_to_be_clickable((By.XPATH,x_path1))).click()
            time.sleep(60)


            for i in range(1,10):
                 js="var q=document.documentElement.scrollTop=300000"
                 browser.execute_script(js)
                 browser.implicitly_wait(15)

            time.sleep(60)

            soup=BeautifulSoup(browser.page_source,"html5lib")
            index=1
            doi=[]
             #根据每篇文章的wrap div标签个数判断每年的论文数
            div_paper=[]
            div_paper=soup.find_all("div",attrs={"ng-repeat":"pub in pubs","class":"pub ng-scope" })
            print(len(div_paper))

            while(index<=len(div_paper)):
                 selector_path='#year > div.ng-isolate-scope > div:nth-of-type('+str(index)+')'

                 selector=selector_path+' a'
                 tag_a=soup.select(selector)
                 #[class="ng-scope"]  [ng-repeat="author in ::pub.authors.slice(0,10)"]
                 selector1=selector_path+' span[ng-repeat^="author in ::pub.authors.slice(0"]'
                 #print(selector1)
                 author_tag_list=soup.select(selector1)
                 temp_author=''
                 author_order = ''
                 author_index=1
                 for author_tag in author_tag_list:
                     #print(author_tag)
                     content_in_tag=author_tag.get_text()
                     if  'txt-color-red' in author_tag.a.get('class') and 'bold' in author_tag.a.get('class'):
                        author_order=str(author_index)

                     temp_index= content_in_tag.find(',')
                     temp_author=temp_author+","+content_in_tag[:temp_index]
                     author_one=process_str(str(content_in_tag[:temp_index]))
                     if operator.eq(name_pinyin, author_one) or operator.eq(name_pinyin_reverse, author_one):
                         author_order = str(author_index)

                     author_index=author_index+1
                 title=''

                 cited_number=''
                 publication=''
                 doi_link=''
                 author=temp_author.strip(',')
                 title=tag_a[0].get_text()
                 if((title[-1]  in string.punctuation)|(title[-1]=='。')):
                       title=title[:-1]
                 for tag in tag_a:
                     text=tag.get_text()
                     regex=re.compile("^ *Cited *by *\d+$")
                    # print(tag) 测试用
                     class_list=tag.get('class')
                     if(type(class_list)==list):
                         if(operator.eq(class_list[0],"ng-binding") and (len(class_list)==1)):
                             publication=tag.get_text();
                     if(re.match(("^ *Cited *by *\d+$"),text,re.RegexFlag.I)):
                         cited_number=re.search("\d+",text).group()
                         #print(tag.get_text())

                     if(operator.eq(tag.get('ng-mouseover'),"show=true")):
                         temp_link=tag.get('href')
                         if(re.match("^http://dx.doi.org/",temp_link)):
                             doi_link=temp_link
                 print('title=',end='')
                 print(title)
                 print('cited_number=',end='')
                 print(cited_number)
                 print('publication=',end='')
                 print(publication)
                 print('author=', end='')
                 print(author)
                 doi=''
                 if(doi_link):
                     doi=doi_extract(doi_link)
                 print('doi=',end='')
                 print(doi)
                 df_temp.loc[index]=[title,doi,publication,cited_number,author,author_order]
                 index=index+1
            df_temp.to_excel(output_path,columns=['title','doi','publication','cited number in Aminer','author','author_order']);
            number=number+1
    browser.quit()
def process_str(str_temp):
    if str_temp:
        str1=str_temp.strip()
        str1 = str1.lower()
        str1 = re.sub(r"\s+",' ',str1)#将字符串中多个空格替换为1个
        return str1
if __name__ == '__main__':                        
    result_path="F:\\jieqing\\computer_result"+"2018"+"\\Aminer"
    if not os.path.isdir(result_path):
        os.makedirs(result_path)
    name='joejoe'
    url='https://www.aminer.cn/profile/minghui-zhou/53f43774dabfaee02acd393d'
    spider_titleDOI_Aminer(url,name,result_path)
