#coding:utf8
'''
Created on 2018年9月17日

@author: Administrator
'''
import selenium 
from selenium.webdriver.support.ui import  Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.common.by import By
import os
import re
import urllib
from bs4 import BeautifulSoup
import operator
from selenium import webdriver
import  http.cookiejar 


url="https://scholar.google.com.hk/citations?user=D3nE0agAAAAJ&hl=zh-CN"
browser=webdriver.Chrome()
browser.get(url)
wait_result = WebDriverWait(browser, timeout=2000, poll_frequency=2,  ignored_exceptions=None).until(
     EC.text_to_be_present_in_element((By.XPATH,'//*[@id="gsc_a_b"]/tr[1]/td[1]/a'), u''))  
for i in range(10):
    browser.find_element_by_xpath('//*[@id="gsc_bpf_more"]').click()#点击页面底部的展开按钮


