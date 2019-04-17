# coding:utf8
'''
Created on 2018年8月9日

@author: Administrator
'''
import re
import os
from pandas.core.frame import DataFrame 
import openpyxl 
from itertools import islice
import re
import operator
import spider_ws_doiORtitle
#http://dx.doi.org/null
def doi_extract(doi_link):
    doi=[]
    for item in doi_link:
        if item:
            temp=re.match("https?://dx.doi.org/(.+)",item.strip())
            temp_doi=temp.group(1)
            doi.append(temp_doi)
        else:
            doi.append("null")
    return doi;        
def process_data():           
    source_path="F:\\jieqing\\computer_result2017"
    dir=os.listdir(source_path)#杰青名单
    output_path="F:\\jieqing\\computer_result2017_paper"
    print(dir)
    unfind_dir="F:\\jieqing\\unfind_dir"
    if not os.path.isdir(unfind_dir):#文件夹用于存储未找到的论文信息
           os.makedirs(unfind_dir)
    for index in range(0,len(dir)):
        #处理收集到的杰青数据，目录下文文件夹以杰青名字命名
       output_dir_name= output_path+"\\"+dir[index]
       if not os.path.isdir(output_dir_name):
           os.makedirs(output_dir_name)
       unfind_dir_name=unfind_dir+ "\\"+dir[index]
       if not os.path.isdir(unfind_dir_name):
           os.makedirs(unfind_dir_name)
           #在"F:\jieqing\unfind_dir"文件夹下生成以杰青名字命名的文件夹
       path=source_path+"\\"+dir[index]
       year_dir=os.listdir(path)#杰青名单下年份目录
       print("year_dir=")
       print(year_dir)
       column_name=['title','doi','year']
       temp_df=DataFrame(columns=column_name);
       #用于记录在web of science没有找到的论文信息
       for year_index in range(0,len(year_dir)):
           temp=re.match("(\w+).xlsx",year_dir[year_index])
           year=temp.group(1)
           
           output_dir_yearOfName = output_dir_name+"\\"+year#在名单下按照年份生成文件夹
           if not os.path.isdir(output_dir_yearOfName):
               os.makedirs(output_dir_yearOfName)
           
           wb=openpyxl.load_workbook(source_path+"\\"+dir[index]+"\\"+year_dir[year_index])
           sheet_names=wb.sheetnames;
           sheet=wb[sheet_names[0]]
           ws=wb.active
           data=ws.values
           col_names = next(data)[1:]
           print(col_names)
           data=list(data)
           idx = [r[0] for r in data]
           data=(islice(r,1,None) for r in data)
           df = DataFrame(data,index=idx,columns=col_names)
          # print(df)
           doi_link=df['doi']
           doi=doi_extract(doi_link)
           print(doi)
           title=df['title']
           print(title)
           download_each_year(doi,title,year,output_dir_yearOfName,temp_df)
           
def download_each_year(doi,title,year,dirname,df):#根据名单下每个年份的论文数据（doi和论文title爬取论文
    i=0;
    downloadID=1;
    for doi,title in zip(doi,title):
        list=[]
        download=spider_ws_doiORtitle.spider_ws_doiORtitle(title,doi,dirname,downloadID)
        #downloadID 表示在当前年份中下载到第几篇文章
        if(download==0):#在web of science中没有找到论文
            list.append(title,doi,year) 
            df.loc[i]=list
            i=i+1;
        else:
            downloadID=downloadID+1

    
if __name__ == '__main__':  
    process_data();   
           
        
        
       
       
    