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
import traceback
from fake_useragent import UserAgent


#2. 研究如何加入日志，已备后续更新或者出错时使用:
    #日志内容：文件名称、修改时间、各章节位置、最新章节、大小、错误报告
#3. 研究如何设定超过重试次数记录
#4. 对过长小说的处理，更换端口或什么方式？
#总有保存为0kb的文件，查找问题所在。好像解决了，由于page+1后的一直和第一页相同所以一直没有读取完第一章
#总有本来可以正常进行确没有写入或写入完全的部分，检查是否是由于进程过多或什么原因导致的

##/#


headers = {'User-Agent' : 'Mozilla/4.0'}
requests.adapters.DEFAULT_RETRIES = 20 # 增加重连次数
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
    req0 = urllib.request.Request(url0)

    response=requests.get(url0)
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

        title = re.sub(u"([^\u4e00-\u9fa5\u0030-\u0039\u0041-\u005a\u0061-\u007a])", "", title)

    
        #新建小说文件
        dl_1=re.findall(r'<ul class="lb fk">.*?<a class="last tb">',html,re.S)[0]
            #print(dl)
        chapter_info_list_1=re.findall(r'<a href="(.*?)"  class="xbk">(.*?)</a>',dl_1)
        print(len(chapter_info_list_1))
        if len(chapter_info_list_1) <= 5:
            raise Exception('too small')
        else:
            
            fb = open("%s\\%s.txt" %(dirname,title), 'w', encoding='utf-8')
            fb.write(url0)
            fb.write('\n')
        #读取分页列表
        pl=re.findall(r'<div class="fy">.*?</li>',html,re.S)[0]
        #print(html)
        chapter_page_list=re.findall(r'<li><a href=(.*?)class="xbk">',pl)
        for idx, item in enumerate(chapter_page_list):
            chapter_page_list[idx]="http://wap.shushuwuxs.org%s " % item
            chapter_page_list[idx]=chapter_page_list[idx].replace(' ','')
            chapter_page_list[idx]=chapter_page_list[idx].replace('\"','')


        chapter_page_list.insert(0,url0)
        print(chapter_page_list)

        for chapter_page in chapter_page_list:

            err_flag1 = 1;
            while err_flag1:
                try:
                    page_response=requests.get(chapter_page, timeout=10,headers=headers)

                except Exception:
                    print('page_message timeout err')
                    pass
                else:
                    err_flag1 = 0;


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
                err_flag2=1;
                err__chapter_log=0;
                while err_flag2:

                    try:
                        chapter_response = requests.get(chapter_url, timeout=10, headers=headers)
                    except Exception:
                        print(title,'chapter timeout err')
                        err__chapter_log=err__chapter_log+1
                        print('err_chapter_time is',err__chapter_log)
                        pass
                    else:
                        err_flag2=0
                chapter_response.encoding='gbk'
                chapter_html=chapter_response.text
                chapter_content=re.findall(r'<article id="nr">(.*?)<div id="zuoyoufy">',chapter_html,re.S)[0]
                # 清理
                page=2#检测空白页
                chapter_response_temp_previous = '123'
                while page <9999:
                    err_page_log=0;

                    try:
                        # t1 = threading.Timer(10, thread_Timer)
                        # # 启动线程
                        # t1.start()
                        chapter_url_temp = chapter_url.replace('.html', '_%i.html' % page)
                        print(chapter_url_temp)
                        chapter_response_temp = requests.get(chapter_url_temp, timeout=(10,15),headers=headers)

                        chapter_response_temp.encoding = 'gbk'
                        chapter_html_temp = chapter_response_temp.text
                        chapter_content_temp=re.findall(r'<article id="nr">(.*?)<div id="zuoyoufy">', chapter_html_temp, re.S)[0]
                        #print(chapter_content_temp[1:100])
                        #print(chapter_response_temp_previous[1:100])
                        if chapter_response_temp_previous== chapter_content_temp:
                            print('same a previous page, jump to next chapter')
                            page_end = page-1
                            page = 10000

                        elif len(chapter_content_temp) < 30:
                            raise pageError('no page')

                        else:
                            chapter_content=chapter_content+chapter_content_temp
                            chapter_response_temp_previous=chapter_content_temp
                            page+=1

                    except requests.exceptions.RequestException as e1:
                        print(title,'Exception：read page time out :',e1)
                        err_page_log=err_page_log+1
                        print('re-conect times = ', err_page_log)
                        print(chapter_url_temp)
                        time.sleep(3)
                        pass

                    except pageError as e2:
                        print(title,'Exception：%s' % e2)
                        page_end=page
                        page=10000
                    except :
                        e_type, e_value, e_traceback = sys.exc_info()
                        print("type ==> %s" % (e_type.__name__))

                        print('error in ', chapter_url_temp)
                        traceback.print_exc()
                        #print("value ==> %s" % (e_value.message))

                        #print("traceback ==> line no: %s" % (e_traceback.tb_lineno))

                        #print("traceback ==> function name: %s" % (e_traceback.tb_frame.f_code.co_name))

                        #print(title,'Exception：%s' % e3)
                        pass

            #预处理回车    
                chapter_content = re.sub('[\001\002\003\004\005\006\007\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1a]+', '', chapter_content)
                chapter_content = chapter_content.replace('&nbsp;', '')
                chapter_content = chapter_content.replace('        ', '')
                chapter_content = chapter_content.replace('\n', '')
                chapter_content = chapter_content.replace('<br />', '')
                chapter_content = chapter_content.replace('&amp;t;', '')
                chapter_content = chapter_content.replace('<br/><br/>', '\n')
                chapter_content = chapter_content.replace('<br/>', '')
                chapter_content = chapter_content.replace('&lt;', '')
                chapter_content = chapter_content.replace('fontsize=&quot;', '')
                chapter_content = chapter_content.replace('&gt;', '')
                chapter_content = chapter_content.replace('&quot', '')

                chapter_content = chapter_content.replace('看~精`彩~小`說~盡`在&#039;wwｗ点０１bｚ点ｎet第&#039;壹~版-主`小&#039;說', '')
            

                #保存至本地    
                fb.write(chapter_title)
                fb.write('\n')
                fb.write(chapter_content)
                fb.write('\n')
               
                print(chapter_url,chapter_title)
                print(page_end,len(chapter_content))
                fb.flush()





        fb.close()
        print(title, 'is over')
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
    #sites.append('http://wap.shushuwuxs.org/booklist/25/')
    for s in range(890,2000):
        sites.append('http://wap.shushuwuxs.org/booklist/%i/'%s)

    start_time = time.perf_counter()
    download_art("http://wap.shushuwuxs.org/booklist/620/")
    #download_all(sites)
    end_time = time.perf_counter()
    print(f'Download {len(sites)} sites in {end_time - start_time} seconds')

if __name__ == '__main__':
    main()

