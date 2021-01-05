import urllib
import urllib.request
from bs4 import BeautifulSoup
import re
import random
import time
import requests
import os
import threading
import time
import concurrent.futures
import sys

<<<<<<< HEAD
#尝试将其在github上发布
=======

>>>>>>> 27ea5bea44854f5291bf88824e0a6e31da9e2fe8
exitFlag = 0

class pageError(Exception):
    def __init__(self, msg):
        self.msg = msg

        def __str__(self):
            return self.msg

# def thread_Timer():
#     raise time_Exception()
#     print("超时")
#     # 创建并初始化线程


def download_art(url0):
    # 设置目标url，使用urllib.request.Request创建请求
    #url0 = "http://wap.shushuwuxs.org/booklist/7984/"
    headers = {'User-Agent' : 'Mozilla/4.0'}
    req0 = urllib.request.Request(url0)
    proxy = '218.59.139.238:80'
    proxies = {
    'http': 'http://' + proxy,
    'https': 'https://' + proxy}

    #response=requests.get(url0,headers=headers,proxies=proxies)
    response=requests.get(url0,headers=headers)
    response.encoding='gbk'

    html=response.text
    
    dirname, filename = os.path.split(os.path.abspath(sys.argv[0])) 
    root=os.path.realpath(sys.argv[0])
    print(root)
    #print(html)
    #读取小说名称
    try:
        title=re.findall(r'<div class="zhong">(.*?)</div>',html)[0]
        print(title)

    
    
        #新建小说文件
        dl_1=re.findall(r'<ul class="lb fk">.*?<a class="last tb">',html,re.S)[0]
            #print(dl)
        chapter_info_list_1=re.findall(r'<a href="(.*?)"  class="xbk">(.*?)</a>',dl_1)
        print(len(chapter_info_list_1))
        if len(chapter_info_list_1) <= 5:
            raise Exception('too small')
        else:
            
            fb = open("%s\\%s.txt" %(dirname,title), 'w', encoding='utf-8')

        #读取分页列表
        pl=re.findall(r'<div class="fy">.*?</li>',html,re.S)[0]
        chapter_page_list=re.findall(r'</a><li><a href=(.*?)class="xbk">',pl)
        for idx, item in enumerate(chapter_page_list):
            chapter_page_list[idx]="http://wap.shushuwuxs.org%s " % item
            chapter_page_list[idx]=chapter_page_list[idx].replace(' ','')
            chapter_page_list[idx]=chapter_page_list[idx].replace('\"','')


        chapter_page_list.insert(0,url0)
        #print(chapter_page_list)

        for chapter_page in chapter_page_list:
            #page_response=requests.get(chapter_page,headers=headers,proxies=proxies)
            page_response=requests.get(chapter_page,headers=headers)
            
            page_response.encoding='gbk'

            page_html=page_response.text

            #读取章节目录
            dl=re.findall(r'<ul class="lb fk">.*?<a class="last tb">',page_html,re.S)[0]
            #print(dl)
            chapter_info_list=re.findall(r'<a href="(.*?)"  class="xbk">(.*?)</a>',dl)
            #print(chapter_info_list)
            #分章节下载
            
            for chapter_info in chapter_info_list:
                chapter_url,chapter_title=chapter_info
                chapter_url="http://wap.shushuwuxs.org%s " % chapter_url
                chapter_url=chapter_url.replace(' ','')
                #下载小说内容
                #chapter_response=requests.get(chapter_url,headers=headers,proxies=proxies)
                chapter_response=requests.get(chapter_url,headers=headers)
                chapter_response.encoding='gbk'
                chapter_html=chapter_response.text
                chapter_content=re.findall(r'<article id="nr">(.*?)<div id="zuoyoufy">',chapter_html,re.S)[0]
                #print('first page')
                page=2#检测空白页
                while page <9999:
                    try:
                        # t1 = threading.Timer(10, thread_Timer)
                        # # 启动线程
                        # t1.start()
                        #预处理
                        chapter_url_temp = chapter_url.replace('.html', '_%i.html' % page)
                        chapter_response_temp = requests.get(chapter_url_temp, timeout=15,headers=headers)
                        #chapter_response_temp = requests.get(chapter_url_temp, timeout=15,headers=headers,proxies=proxies)
                        #print('next page')
                        chapter_response_temp.encoding = 'gbk'
                        chapter_html_temp = chapter_response_temp.text
                        chapter_content_temp=re.findall(r'<article id="nr">(.*?)<div id="zuoyoufy">', chapter_html_temp, re.S)[0]
                        if len(chapter_content_temp)<30:
                            raise pageError('no page')
                        else:
                            chapter_content=chapter_content+chapter_content_temp
                            page+=1

                    except requests.exceptions.RequestException as e1:
                        pass
                        print('Exception：time out')

                    except pageError as e2:
                        print('Exception：%s' % e2)
                        page_end=page
                        page=10000
                    except Exception:
                        pass
            
            # # 清理    
                chapter_content = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', chapter_content)
                chapter_content = chapter_content.replace('&nbsp;', '')
                chapter_content = chapter_content.replace('        ', '')
                chapter_content = chapter_content.replace('\n', '')
                chapter_content = chapter_content.replace('<br />', '')
                chapter_content = chapter_content.replace('&amp;t;', '')
                chapter_content = chapter_content.replace('<br/><br/>', '\n')
                chapter_content = chapter_content.replace('<br/>', '')
                chapter_content = chapter_content.replace('看~精`彩~小`說~盡`在&#039;wwｗ点０１bｚ点ｎet第&#039;壹~版-主`小&#039;說', '')
            

                #保存至本地    
                fb.write(chapter_title)
                fb.write('\n')
                fb.write(chapter_content)
                fb.write('\n')
               
                print(chapter_url,chapter_title)
                print(page_end,len(chapter_content))





        fb.close()
    except Exception as e:
        print('Exception：%s' % e)







def download_all(sites):
    # 并发模式,创建了一个线程池，总共有5个线性可以分配使用
   # with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
   # 对sites中的每个元素，并发地调用函数download_one
   #     executor.map(download_art, sites)
    # 并行模式,创建进程池，系统自动返回CPU的数量作为可以调用的进程
    with concurrent.futures.ProcessPoolExecutor() as executor:
         executor.map(download_art, sites)




def main():
    sites = []
    for s in range(1,1000):
        sites.append('http://wap.shushuwuxs.org/booklist/%i/'%s)

    start_time = time.perf_counter()
    #download_art("http://wap.shushuwuxs.org/booklist/1/")
    download_all(sites)
    end_time = time.perf_counter()
    print(f'Download {len(sites)} sites in {end_time - start_time} seconds')

if __name__ == '__main__':
    main()