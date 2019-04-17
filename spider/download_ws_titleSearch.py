#coding:utf8
import os
import re

import requests
import  http.cookiejar 
import urllib
import operator
from selenium import webdriver
import string
#因为web of science的搜索结果列表页面仅提供对核心数据库的论文全纪录和全纪录与引用的参考文献的下载
#搜索方式标题

def init(search_url,title): 
    cookie=http.cookiejar.CookieJar()
    pro_cookie=urllib.request.HTTPCookieProcessor()
    opener=urllib.request.build_opener(pro_cookie)
    product=getProduct(search_url)
    SID  = getSID(search_url);
    Referer_url='http://apps.webofknowledge.com/UA_GeneralSearch_input.do?product={}&search_mode=GeneralSearch&SID={}&preferencesSaved='.format(product,SID);               
    opener.addheaders = [('Host','apps.webofknowledge.com'),
                        ('Connection','keep-alive'),
                       ('Upgrade-Insecure-Requests','1'),
                       ('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'),
                       ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'),
                       ('Accept-Encoding','gzip, deflate'),
                       ('Accept-Language', 'zh-CN,zh;q=0.9'),
                       #('Referer',Referer_url)
                       ]
        
    
    print("SID=",end='')
    print(SID)
    text = opener.open(search_url,timeout = 50).read().decode("utf8")
  #  print text
    QID = getQID(text)
    print("QID=",end='')
    print(QID)
    parentQid = getparentQid(text)
                                                                                                      
    PageNum,PaperNum = getPageNum_PaperNum(text)#得到页数和文章数
    print("PageNum=",PageNum)#结果列表显示所需页数
    print("PaperNum=",PaperNum)#结果列表文章数
    show_paper_num=getShowNum(text)
    print('show_paper_num=',show_paper_num)#每页显示的文章数
    
    page_id=getPage_id(text);#获取起始页面
    
    id=get_paper_id(text,title)#所搜素的文章位于当前页面第几个
    
    for num in range(page_id+1,PageNum+1):
        next_url = 'http://apps.webofknowledge.com/summary.do?product={}&search_mode=GeneralSearch&parentQid=&qid={}&SID={}&&update_back2search_link_param=yes&page={}'.format(product,QID,SID,num)
        temp_text = opener.open(next_url,timeout = 50).read().decode("utf8")
        if(id==0):
            id=get_paper_id(temp_text,title)
            page_id=page_id+1#所搜素的文章位于第几个页面
        else:
            break;
    print('page_id=',page_id)
    doc_id=id+(page_id-1)*show_paper_num
    print("doc_id=",doc_id)
    
    return product,QID,SID,page_id,doc_id
    
   
     
def get_paper_id(text,title1):#这个程序用于获取页面上与title匹配的标题，返回该标题在当前页面的序号
    title_list=re.findall(r'<value lang_id="">(.*?)</value>',text,flags=re.RegexFlag.S)
    
    #print(len(title_list))
    title_page=[]
    for str1 in title_list:#移除匹配匹配标题中对某些词装饰的标签
        str1=str1.replace('<span class="hitHilite">',' ')
        str1=str1.replace('</span>',' ')
        str1=str1.replace('\n',' ')
        title_page.append(str1)
        #print("str1=",end='')
        #print(str1)
    title=str_process(title1)
    id=1;
    print(title_page)
    for str in title_page:
        str=str_process(str)
        print("str=",end='')
        print(str)
        if(operator.eq(str,title)):
            return id 
        id=id+1 
    else:
        id=0 
        return id
def  str_process(str_temp):  #对字符串进行处理
    temp=str_temp.strip();#去除字符串收尾的空格
    temp=re.sub(r"\s+",' ',temp)#将字符串中多个空格替换为1个
    temp=re.sub(r"\s+\,\s+",',',temp)#去除逗号前后的多余空格
    temp=re.sub(r"\s*\-\s*",'-',temp)#去除‘-’前后的多余空格
    temp=temp.lower()
    temp=temp.strip(string.punctuation)
    return temp
def getShowNum(text):
    #<span class="select2-selection__rendered" id="select2-selectPageSize_bottom-container" title=""每页 10 条 </span>
    m1=re.search(r'<option value="\d+" selected="selected">\s*每\s*页\s* (\d+)\s*条\s*</option>',text)
    #print(m1)
    return int(m1.group(1))
   #<input aria-label="浏览至特定检索结果页面" class="goToPageNumber-input" type="text" name="page" value="(\d+)" size="5" style="width:40px;" tabindex="0">
   
def  getPage_id(text):#获取起始页面
     m=re.search('<input aria-label="浏览至特定检索结果页面" class="goToPageNumber-input" type="text" name="page" value="(\d+)".*?/>',text)
     return int(m.group(1))
def getPageNum_PaperNum(text):
    m1 = re.search("handle_nav_final_counts\(.*?\);",text)
    m2 = re.search("\('(.*?)', '(.*?)'\)",m1.group(0))
    return int(m2.group(2).replace(',','')),int(m2.group(1).replace(',',''))
def getProduct(url):
    a = re.search('product=(.*?)&',url)
    return a.group(1)
def getSID(url):
    a = re.search('SID=(.*?)&',url)
    return a.group(1)
def getQID(text):
    a = re.search('<input type="hidden" name="qid" value="(.*?)"/>',text)
    #<input type="hidden" name="qid" value="1"/>
    return a.group(1)
def getparentQid(text):
    a = re.search('<input type="hidden" name="parentQid" value="(.*?)" />',text)
    return a.group(1)

def download2(driver,search_url,dirname):
    product,QID,SID,page_id,doc_id=init(search_url,title)
    
#主要原理：利用selenium模拟点击的方式实现
    paper_url='http://apps.webofknowledge.com/full_record.do?product={}&search_mode=GeneralSearch&qid={}&SID={}&page={}&doc={}'.format(product,QID,SID,page_id,doc_id)
    driver.get(paper_url)
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('/html/body/div[2]/div[26]/div/div/div/div[4]/span/span/span[1]/span/span[2]').click();
    #点击上方选择保存格式
    driver.find_element_by_xpath('//*[@id="select2-saveToMenu-results"]/li[4]').click();
    #点击选择  保存为其它文件格式
    driver.find_element_by_xpath('//*[@id="select2-saveToMenu-container"]')
   
    driver.find_element_by_xpath('//*[@id="ui-id-5"]/form/div[4]/span/button').click()
    driver.implicitly_wait(5)
def download1(search_url,title,dirname,file_name):
#主要原理：
#利用Fiddler抓包工具，查看请求网页的head和body内容
#p_dict中的内容主要是依据body中内容
#指定了下载文件的名字 file_name
#该程序有错误，需要修改
    product,QID,SID,page_id,doc_id=init(search_url,title)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)
    output_path = os.path.join(dirname, file_name+'.txt')
   
    #first_url='http://apps.webofknowledge.com/full_record.do?product=UA&search_mode=GeneralSearch&qid={}&SID={}&page={}&doc={}'.format(QID,SID,page_id,doc_id),
                
    session = requests.session()
    header1 = {  
                'Host': 'apps.webofknowledge.com',
                'Content-Type': 'application/x-www-form-urlencoded',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            #    'Referer': url,
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,zh;q=0.9',
                'Connection': 'keep-alive'
                }
      
   
    header2 = {'Host':'ets.webofknowledge.com', 
              'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:40.0) Gecko/20100101 Firefox/40.0',
               'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
               'Accept-Encoding': 'gzip, deflate',
             #  'Referer':url,
               'Connection':'keep-alive'}


    temp_rurl='http%3A%2F%2Fapps.webofknowledge.com%2Fsummary.do%3Fproduct%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26product%3DWOS%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26search_mode%3DGeneralSearch%26qid%3D1%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}%26SID%3D{}'
    temp_rurl=temp_rurl.replace("{}",SID)
    #cookies = {'SID':SID,"CUSTOMER":"Dalian University of Technology","E_GROUP_NAME":"Dalian University of Technology"}
    cookies = {'SID':SID}
    first_url='http://apps.webofknowledge.com/OutboundService.do?action=go&&&marked_list_candidates={}&excludeEventConfig=ExcludeIfFromFullRecPage'.format(doc_id)
             
    p_dict = {}
    p_dict['displayCitedRefs']='true'   
    p_dict['displayTimesCited']='true'   
    p_dict['displayUsageInfo']='true' 
    p_dict['viewType']='fullRecord'
    p_dict['product']=product
    p_dict['rurl']="http%3A%2F%2Fapps.webofknowledge.com%2Ffull_record.do%3Fsearch_mode%3DGeneralSearch%26qid%3D{}%26log_event%3Dyes%26product%3D{}%26SID%3D{}%26viewType%3DfullRecord%26doc%3D{}%26page%3D{}".format(QID,product,SID,doc_id,page_id)
    #p_dict['rurl']='http%3A%2F%2Fapps.webofknowledge.com%2Ffull_record.do%3Fsearch_mode%3DGeneralSearch%26qid%3D5%26log_event%3Dyes%26product%3DUA%26SID%3D6D9aKCpki5LpQTgznEI%26viewType%3DfullRecord%26doc%3D1%26page%3D1'
    p_dict['mark_id']='UDB'
    p_dict['colName']=''#这个数据因论文不同而不同，表示论文入藏号前的数据库名字，错误书写会引起错误
    p_dict['search_mode']='GeneralSearch'
    p_dict['locale']='zh_CN'
    p_dict['recordID']=''#这个数据因论文不同而不同，可以省略
    p_dict['view_name']='UA-fullRecord'
    #p_dict['sortBy']='RS.D;PY.D;AU.A;SO.A;VL.D;PG.A' 
    p_dict['sortBy']='PY.D;LD.D;SO.A;VL.D;PG.A;AU.A'
    p_dict['mode']='OpenOutputService'
    p_dict['qid']=QID
    p_dict['SID']=SID  
    p_dict['format']="saveToFile"
    p_dict['filters']=''
    #p_dict['filters']='HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSN PUBINFO KEYWORDS CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS'
   # p_dict['filters']='HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSN PUBINFO CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE CONFERENCE_INFO SOURCE ABSTRACT TITLE AUTHORS KEYWORDS'  
                #       HOT_PAPER HIGHLY_CITED OPEN_ACCESS USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY PAGEC ISSN CITTIMES CITREFC ADDRS KEYWORDS DOCTYPE LANG ABSTRACT SOURCE TITLE AUTHORS  
    
    #这里的各项数据表示请求的文献的各项信息，摘要，标题，作者，关键词等（ABSTRACT TITLE AUTHORS KEYWORDS）
    #ACCESSION_NUM 入藏号     CITREFC引用的参考文献数量
    '''source表示如下信息
        Computer Science
                        计算机科学
                        卷:44 期:12 页:255-259
                        文献号:1002-137X(2017)44:12<255:JYJZFJ>2.0.TX;2-R     
                        出版年:2017    
                        文献类型:Article
                        对应下载文件中的如下信息
            Z3 计算机科学
            SO Computer Science
            VL 44
            IS 12
            BP 255
            EP 259
            AR 1002-137X(2017)44:12<255:JYJZFJ>2.0.TX;2-R
            PY 2017
   '''
    p_dict['mark_to']=doc_id
    p_dict['mark_from']=doc_id
    p_dict['queryNatural']='<b>标题:</b> (learning  to  rank)'#这个数据可以省略，无关紧要
    p_dict['count_new_items_marked']= 0
    p_dict['use_two_ets']='false'
    p_dict['IncitesEntitled']='yes'
   
    #p_dict['fields_selection']='HIGHLY_CITED HOT_PAPER OPEN_ACCESS PMID USAGEIND AUTHORSIDENTIFIERS ACCESSION_NUM FUNDING SUBJECT_CATEGORY JCR_CATEGORY LANG IDS PAGEC SABBR CITREFC ISSM PUBINFO KEYWORDS CITTIMES ADDRS CONFERENCE_SPONSORS DOCTYPE ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS'  
                    
                    

    p_dict['fields_selection']=''
    p_dict['save_options']='othersoftware'    
    r1 = session.post(first_url, headers = header1,cookies = cookies, data = p_dict,allow_redirects = False)
    

    location = r1.headers['location']
    print(r1.headers['set-cookie'])
    print(r1.headers['set-cookie'].split('='))
    jsessionid = r1.headers['set-cookie'].split('=')[1]
    
    jsessionid = jsessionid.split(';')[0]
    #print jsessionid
    cookies['JSESSIONID'] = jsessionid
    print ('location', r1.headers['location'])
    #print 'cookies', requests.utils.dict_from_cookiejar(session.cookies)
#     #login_url = r1.url
#     #login_url = 'http://ets.webofknowledge.com/ETS/ets.do?refineString=null&rurl=http%253A%252F%252Fapps.webofknowledge.com%252Fsummary.do%253FSID%253D3FBCQHo7bvU816yo5LX%2526product%253DWOS%2526parentQid%253D1%2526parentProduct%253DWOS%2526qid%253D86%2526search_mode%253DCitingArticles&displayUsageInfo=true&qid=103&mark_to=10&fileOpt=othersoftware&displayCitedRefs=true&totalMarked=10&SID=3FBCQHo7bvU816yo5LX&product=UA&mark_from=1&parentQid=70&displayTimesCited=true&sortBy=PY.D;LD.D;SO.A;VL.D;PG.A;AU.A&timeSpan=null&UserIDForSaveToRID=null&action=saveToFile&colName=WOS&filters=PMID AUTHORSIDENTIFIERS ACCESSION_NUM ISSN CONFERENCE_SPONSORS ABSTRACT CONFERENCE_INFO SOURCE TITLE AUTHORS  '.format(SID,end,start-end+1,SID,start)
#     #print login_url
    r = session.get(location,headers = header2,cookies = cookies, stream=True) 
    with open(output_path, 'wb') as fd: 
        for chunk in r.iter_content(chunk_size=1024): 
            fd.write(chunk)

  
def start_download(driver,search_url,title,dirname,filename,type):
    print('start to crawl'+':  '+title)
    if(type==1):
        download1(search_url,title,dirname,file_name)
        print(dirname + ':has been done')  
    elif(type==2):
        download2(driver,search_url,dirname)
        print(dirname + ':has been done')
    else:
        return 0
    
if __name__ == '__main__':
    search_url = r'http://apps.webofknowledge.com/Search.do?product=UA&SID=5DFYXwpvhUwLCWdF4Hi&search_mode=GeneralSearch&prID=77beef33-b838-4efa-bb9a-9251bb664fd4'
    dirname = 'F://test'
    title="Balancing Speed and Quality in Online Learning to Rank for Information Retrieval"
    file_name="paper"+str(1)
    driver=webdriver.Chrome()
    driver.get(search_url)
    start_download(driver,search_url, title, dirname,file_name,2)
    
