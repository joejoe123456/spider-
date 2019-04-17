#coding:utf8
'''
Created on 2018年10月5日

@author: Administrator
'''
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import  WebDriverWait
from selenium.webdriver.common.by import By
import selenium
import re
import operator
from bs4 import BeautifulSoup
import os 
import lxml
import string 
from pandas.core.frame import DataFrame 

def process_str(str_temp):
    if str_temp:
        str1=str_temp.strip()
        str1 = str1.lower()
        str1 = re.sub(r"\s+",' ',str1)#将字符串中多个空格替换为1个
        return str1
def spider_titleDOI_dblp(url,name,name_pinyin,result_path,df_map):
    author_path=result_path+'\\'+name
    name_pinyin = process_str(name_pinyin)
    name_pinyin_list = name_pinyin.split()
    name_pinyin_list.reverse()
    name_pinyin_reverse = (' ').join(name_pinyin_list)
    if not os.path.isdir(author_path):
        os.makedirs(author_path)
    
    browser=webdriver.Chrome()
    browser.get(url)
    browser.implicitly_wait(30);
    for i in range(1,10):
        js="var q=document.documentElement.scrollTop=300000"
        browser.execute_script(js)
        browser.implicitly_wait(15)
    #soup=BeautifulSoup(browser.page_source,"html5lib")
    text=browser.page_source;
    #print(text)
    #html_text_removed=re.findall(r'<li class="year">2018</li>(.*?)<li class="year">2016</li>',text,flags=re.RegexFlag.DOTALL)
    
    year=re.findall(r'<li class="year">(\d+?)</li>',text,flags=re.RegexFlag.DOTALL)
    year_len=len(year)
    first_num=int(year[0])
    second_num=int(year[1])
    
    for each_year in year[2:]:
        if(second_num<=2016 and first_num>2016):
            break;
        else:
            first_num=second_num
            second_num=int(each_year)
        
    regex_string='<li class="year">{}</li>(.*?)<li class="year">{}</li>'.format(year[0],str(second_num))        
    html_text_removed=re.findall(regex_string,text,flags=re.RegexFlag.DOTALL)
    
    #print(html_text_removed)
    #print(len(html_text_removed))
    #print(type(html_text_removed))
    
    paper1_after_2016=re.findall(r'<img alt="" title="Journal Articles" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper2_after_2016=re.findall(r'<img alt="" title="Conference and Workshop Papers" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper3_after_2016=re.findall(r'<img alt="" title="Editorship" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper4_after_2016=re.findall(r'<img alt="" title="Informal and Other Publications" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper5_after_2016=re.findall(r'<img alt="" title="Parts in Books or Collections" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper6_after_2016=re.findall(r'<img alt="" title="Reference Works" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper7_after_2016=re.findall(r'<img alt="" title="Data and Artifacts" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    paper8_after_2016=re.findall(r'<img alt="" title="Books and Theses" src="https://dblp.uni-trier.de/img/n.png"\s*/>',html_text_removed[0])
    remove_num=len(paper1_after_2016)+len(paper2_after_2016)+len(paper3_after_2016)+len(paper4_after_2016)+len(paper5_after_2016)+len(paper6_after_2016)+len(paper7_after_2016)+len(paper8_after_2016)
    paper_after_2016=re.findall(r'<li class="entry (?:informal|article|inproceedings|editor|book|incollection|reference|data) toc" id=.*? itemscope="" itemtype=".*?">.*?</li>',html_text_removed[0])
    #print(remove_num)
    #print(len(paper_after_2016))
    if(len(paper_after_2016)==remove_num):
        
        year_index=0
        for each_year in year:
            year_index=year_index+1
            if int(each_year) <= 2019:
            #if int(each_year)<=2019 and int(each_year)>2016:                     #if(int(each_year)<=2016):
                temp_html=''
                if(year_index<len(year)):
                    string='<li class="year">{}</li>(.*?)<li class="year">{}</li>'.format(each_year,year[year_index])
                    #print(type(string))
                    temp_html=re.findall(string,text,flags=re.RegexFlag.DOTALL)#抽取出每一年论文部分对应的html源码
                else:
                    string='<li class="year">{}</li>(.*?)<em>no results</em>'.format(each_year)
                    temp_html=re.findall(string,text,flags=re.RegexFlag.DOTALL)#抽取出每一年论文部分对应的html源码
                output_path=os.path.join(author_path,str(each_year)+".xlsx")#这个excel文件存储dblp上作者每年的论文信息
                error_path=os.path.join(author_path,str(each_year)+'ERROR'+".txt")#存储出错的文章信息
                #print(temp_html[0])
                df_temp=DataFrame(columns=['title','doi','publication','publication_link','author','author_order'])
                
                '''
                f1 = open("F:\\test\\temp_html.html",'wb+')
                for s in temp_html:
                    f1.write(bytes(s, encoding = "utf8")) 
                f1.close()
                '''
                if(temp_html):
                    xml_link=re.findall('<li><a href="([^\'\"]*?)"><img alt="" src="https://dblp.uni-trier.de/img/xml.dark.16x16.png" class="icon" />XML</a></li>',temp_html[0])#dblp提供的论文的xml描述文件链接
                   # print(xml_link)
                  #  print(len(xml_link))
                    paper_li=re.findall(r'<li class="entry (?:informal|article|inproceedings|editor|book|incollection|reference|data) toc" id=.*? itemscope="" itemtype=".*?">.*?<meta.*?></li>',temp_html[0])
                    '''
                    f = open("F:\\test\\paper_li.html",'wb+')
                    for s in paper_li:
                        f.write(bytes(s, encoding = "utf8")) 
                        f.write(bytes('\n', encoding = "utf8"))
                    f.close()
                    '''
                    if(len(xml_link)==len(paper_li)):
                        remove_unneed(paper_li,xml_link)
                       # print(paper_li)
                        #print(xml_link)
                        #print(len(xml_link))
                    pub_link=[]#存储文章发表期刊或会议的链接
                    for li in paper_li:
                        link=re.findall(r'<span class="title" itemprop="name">.*?</span>\s*<a href="(http[s]?://dblp.uni-trier.de/db.*?)">',li)
                        pub_link.append(link[0])
                   
                    #print(len(pub_link))
                    for xml_url,pub_url in zip(xml_link,pub_link):
                        f_error=open(error_path,'a+')
                        f1=open(author_path+"\\"+"map_error1.txt",'a+',encoding='utf-8')
                        f2=open(author_path+"\\"+"map_error2.txt",'a+',encoding='utf-8')
                        df_map,df_temp=deal_xml(name_pinyin,name_pinyin_reverse,browser,xml_url,pub_url,each_year,df_temp,df_map,f_error,f1,f2,author_path)
                        
                          
                
                    df_temp.to_excel(output_path,columns=['title','doi','publication','publication_link','author','author_order']);
                  #  df_map.to_excel(result_path+'\\'+"map.xlsx");
             
    browser.close();
   
    return df_map;
def remove_unneed(paper_li,xml_link):
    pattern=re.compile('<li class="entry (?:editor|book|reference|data) toc" id=.*? itemscope="" itemtype=".*?">.*?</li>')
    find_list=[li_item for li_item in paper_li if pattern.match(li_item)]
    remove_index=[] 
    for item in find_list:
        remove_index.append(paper_li.index(item)) 
     #   print(paper_li.index(item))
     #   print(item) 
    remove_index.sort(reverse = True)
    for index in remove_index:
        del xml_link[index]
        del paper_li[index]
        
def deal_pub_conf_link(year,url,pub_url,author_path):#获取会议缩写的全名      
    f=open(author_path+"\\"+"conf_缩写.txt",'a+')
    f.write('\n'+str(year).encode('utf8', 'ignore').decode('utf8', 'ignore')+"\t"+str(url).encode('utf8', 'ignore').decode('utf8', 'ignore')+"\t"+str(pub_url).encode('utf8', 'ignore').decode('utf8', 'ignore')+"\t\n")
    f.close();
def deal_pub_journal_link(browser,pub_url):#获取期刊缩写的全名
    browser.get(pub_url)
    browser.implicitly_wait(30)
    soup=BeautifulSoup(browser.page_source,"html5lib")
    h=soup.find('h1')
    text=re.sub(r'<a.*?>','',str(h))
    text=re.sub(r'\n',' ',text)
    text=re.sub(r'<\s*/a>','',text)
    text=re.sub(r'<h1.*?>','',text)
    text=re.sub(r'<\s*h1>','',text) 
    
    publication=''
    publication_temp1=re.match('(.*?)\,\s*Volume',text).group(1).strip()
    publication=publication_temp1
    if(operator.ne(re.search(r'\.',publication_temp1),None)):
         span=soup.find('span',attrs={"itemprop": "name"},string=publication_temp1)  
         a_link=span.find_parent("a")
         link=a_link['href']
         browser.get(link)
         browser.implicitly_wait(30)
         soup1=BeautifulSoup(browser.page_source,"html5lib")
         h=soup1.find('h1')
         text=re.sub(r'<a.*?>','',str(h))
         text=re.sub(r'\n',' ',text)
         text=re.sub(r'<\s*/a>','',text)
         text=re.sub(r'<h1.*?>','',text)
         text=re.sub(r'<\s*h1>','',text) 
         if(operator.ne(re.search('\(.*?\)',text),None)):
            publication=re.match('(.*?)(?=\(.*\))',text) .group(1).strip()
         else:
            publication= text
  #  print(publication)
    return publication

def deal_xml(name_pinyin,name_pinyin_reverse,browser,url,pub_url,year,df_temp,df_map,f_error,f1,f2,author_path):
    df_temp_new=''
    browser.get(url)
    browser.implicitly_wait(30)
    xml=re.findall(r'<dblp.*?>(.*?)</dblp>',browser.page_source,flags=re.RegexFlag.DOTALL)
    soup=BeautifulSoup(xml[0],"xml")
    root_tag=soup.contents[0]
    title=''
    author=''
    author_order=''
    author_tag_list = re.findall(r'<author.*?>(.*?)</author>', xml[0])
    print(author_tag_list)
    author_index=1
    for author_tag in author_tag_list:
        temp_author = re.sub("<.*?>", '', author_tag)
        temp_author = temp_author.strip('？')
        temp_author = temp_author.strip('?')
        temp_author = temp_author.strip('.')
        author_one=process_str(temp_author)
        if operator.eq(name_pinyin, author_one) or operator.eq(name_pinyin_reverse, author_one):
            author_order = str(author_index)
        author = author + "," + temp_author
        author_index= author_index+1
    author = author.strip(',')

    year_xml=root_tag.year.contents[0]
    publication_ab=''
    publication=''
    doi=''
    temp_title=str(root_tag.title)
    if len(root_tag.title.contents)>1:
        temp_title=str(root_tag.title)
        temp_title=re.sub("<.*?>",'',temp_title)
        temp_title=re.sub("\s+-",'-',temp_title)
        title=temp_title
        title = title.strip('？')
        title = title.strip('?')
        title = title.strip('.')

    
    else:
        title=root_tag.title.contents[0].strip('.')
        title=title.strip('？')
        title = title.strip('?')

    if(re.search(r'<journal>',xml[0])):
        publication_ab=root_tag.journal.contents[0].strip()
    elif(re.search(r'<booktitle>',xml[0])):
        #if(re.search(r'<publisher>',xml[0])):
            #publication=(root_tag.publisher.contents[0])+"###"+(root_tag.booktitle.contents[0])
        #else:
       publication_ab=root_tag.booktitle.contents[0].strip()
    # elif(re.search(r'<school>',xml[0])): 博士和硕士论文的publication在此类标签下
        #publication=root_tag.school.contents[0]
    else:
       publication_ab=''
    doi_link= re.findall(r'(https?://doi\.(?:\S+.*\.)?org/(.*)</ee>)',xml[0])
    if(year_xml==year):
        '''
        print('title=',end='') 
        print(title) 
        print('publication=',end='')
        print(publication)
        print(doi_link)
        '''
        doi=''
        if(doi_link):
           doi=doi_link[0][1]
    # print('doi=',end='')
      #  print(doi)
        title_list=list(df_temp['title'])
        #print(title_list)
        new_line=DataFrame({"title":title,"doi":doi,"publication":publication_ab,"publication_link":str(pub_url),'author':author,'author_order':author_order},index=['1'])
        if(title not in title_list):
            df_temp_new=df_temp.append(new_line,ignore_index=True)
        else:
            df_temp_new=df_temp
    else:
        #如果一篇文章的年份信息与xml的年份信息不统一，这个错误将被记录在对应年份的error文本中，2017ERROR.txt
        if(f_error.tell()==0):
            f_error.write("dblp")
            f_error.write("title:"+title+"doi:"+doi)
        else:
            f_error.write("\ntitle:"+title+"doi:"+doi)
        f_error.close()
    if operator.ne(re.search(r'\.\s+',publication_ab),None) or (publication_ab.endswith('.')) or operator.ne(re.search(r'\.:',publication_ab),None) or operator.ne(re.search(r'\.：',publication_ab),None):
        if(operator.ne(re.search(r'https?://dblp.uni-trier.de/db/journals/.*?',pub_url),None)):
            publication=deal_pub_journal_link(browser,pub_url)
            publication_ab_list=list(df_map['publication_ab'])
            publication_list=list(df_map['publication'])
            if((publication_ab not in publication_ab_list)|(publication not in publication_list)):
               if((publication_ab in publication_ab_list) and (publication not in publication_list)):
                  
                   index_temp=publication_ab_list.index(publication_ab)
                   publication_temp= publication_list[index_temp]
                   f1.write("\n"+str(year).encode('utf8', 'ignore').decode('utf8', 'ignore')+":"+title.encode('utf8 ', 'ignore').decode('utf8', 'ignore')+"  "+publication_ab.encode('utf8', 'ignore').decode('utf8', 'ignore')+":"+publication.encode('utf8', 'ignore').decode('utf8', 'ignore')+"----"+publication_temp.encode('utf8', 'ignore').decode('utf8', 'ignore')+"\n")
               if((publication_ab not in publication_ab_list) and (publication in publication_list)):
                   index_temp=publication_list.index(publication)
                   ab_temp= publication_ab_list[index_temp]
                   f2.write("\n"+str(year).encode('utf8', 'ignore').decode('utf8', 'ignore')+":"+title.encode('utf8', 'ignore').decode('utf8', 'ignore')+"   "+publication_ab.encode('utf8', 'ignore').decode('utf8', 'ignore')+":"+publication.encode('utf8', 'ignore').decode('utf8', 'ignore')+"----"+ab_temp.encode('utf8', 'ignore').decode('utf8', 'ignore')+"\n")
               new_line=DataFrame({"publication_ab":publication_ab,"publication":publication},index=['1'])
               df_map=df_map.append(new_line,ignore_index=True)
        if(operator.ne(re.search(r'https?://dblp.uni-trier.de/db/conf/.*?',str(pub_url)),None)):
            deal_pub_conf_link(year,url,pub_url,author_path)
    return df_map,df_temp_new
if __name__ == '__main__': 
    result_path="F:\\jieqing\\temp"
    url='https://dblp.uni-trier.de/pers/hd/w/Wang_0001:Meng'
    name="ghgfh"
    df_map=DataFrame(columns=['publication_ab','publication'])
    spider_titleDOI_dblp(url,name,result_path,df_map)
'''
<img alt="" title="Journal Articles" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Conference and Workshop Papers" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Editorship" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Informal and Other Publications" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Parts in Books or Collections" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Reference Works" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Data and Artifacts" src="https://dblp.uni-trier.de/img/n.png">
<img alt="" title="Books and Theses" src="https://dblp.uni-trier.de/img/n.png">
'''
