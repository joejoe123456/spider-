#coding:utf8
'''
Created on 2018年8月1日

@author: Administrator
'''

from itertools import islice
import openpyxl 
from pandas.core.frame import DataFrame 
import pandas as pd
import os

from merge_dblpAndAminer.xlsx2DataFrame import xlsx2DataFrame
from bs4 import BeautifulSoup
from spider.spider_on_Aminer import spider_titleDOI_Aminer
from spider.spider_on_dblp import spider_titleDOI_dblp
def Aminer_spider(names,names_pinyin,Aminer_urls):
    index=0
    result_path="F:\\jieqing\\computer_result"+"2018"+"\\Aminer_original"
    if not os.path.isdir(result_path):
        os.makedirs(result_path)
    for i in range(2,len(names)+1):#len(names)+1
        url=Aminer_urls[i]
        name=names[i]
        name_pinyin=names_pinyin[i]
        print(url)
        print(name)
        if url:
            spider_titleDOI_Aminer(url,name,name_pinyin,result_path)
def Dblp_spider(names, dblp_urls):
    index=0
    result_path="F:\\jieqing\\computer_result2018\\dblp_original"
    if not os.path.isdir(result_path):
        os.makedirs(result_path)
    if(os.path.isfile("F:\\jieqing\\reference"+"\\"+"map.xlsx")):
        df_map=xlsx2DataFrame("F:\\jieqing\\reference"+"\\"+"map.xlsx")
    else:
        df_map=DataFrame(columns=['publication_ab','publication'])
    for i in range(0,len(names)+1):
        url=dblp_urls[i]
        name=names[i]
        name_pinyin = names_pinyin[i]
        print(url)
        print(name)
        if(url):
            df_map=spider_titleDOI_dblp(url,name,name_pinyin,result_path,df_map)
            print(df_map)
            df_map.to_excel("F:\\jieqing\\reference"+'\\'+"map.xlsx");
        else:
            f=open(result_path+"noDBLPurl.txt",'a+')
            f.write("\n"+name+"的dblp_url为空")
            f.close()
    if not os.path.isdir(result_path+'\\'+"reference"):
        os.makedirs(result_path+'\\'+"reference")
    df_map.to_excel("F:\\jieqing\\reference"+'\\'+"map.xlsx");
if __name__=="__main__":
    wb=openpyxl.load_workbook("F:\\jieqing\\2018computer.xlsx")
    sheet_names=wb.sheetnames;
    sheet=wb[sheet_names[0]]
    ws=wb.active
    data=ws.values
    print(type(data))
    col_names = next(data)[0:]
    print(col_names)
    
    data=list(data)
    
    idx = [x for x in range(1,len(list(data))+1)]
    data=(islice(r,0,None) for r in data)
    df = DataFrame(data,index=idx,columns=col_names)
    print(df)
    
    names=list(df["name"])
    names_pinyin=list(df["name_pinyin"])
    Aminer_urls=list(df["Aminer"])#作者在Aminer上的url
    dblp_urls=list(df["dblp"])
    #Dblp_spider(names, names_pinyin, dblp_urls)
    print(names_pinyin)
    Aminer_spider(names, names_pinyin,Aminer_urls)
     

        
