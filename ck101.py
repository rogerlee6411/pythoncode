#!usr/bin/python
# -*- coding: UTF-8 -*-
#python3.x
# ------ 模块 ------ 
from random import Random #随机数
import re #正则表达式
import urllib.request 
from bs4 import BeautifulSoup as bs  # use BeautifulSoup
#http模块
import http.cookiejar #http-cookie模块
import socket #网络编程模块
import os #操作系统模块
import datetime, time #日期时间模块
try:
    import chardet # html内容分析模块
except ImportError as e:
    chardetSupport = False
else:
    chardetSupport = False
try:
    import concurrent.futures #Python3.2+ 线程池模块
except ImportError as e:
    #print (e)
    import threading #多线程模块
    poolSupport = False
else:
    poolSupport = True

# ----------------------------------------------
# 打印日志
printLogEnabled = True
collectHtmlEnabled = True
timeout = 30
socket.setdefaulttimeout(timeout)
thePoolSize = 300

def makeOpener(head={
    'Connection': 'Keep-Alive',
    'Accept': 'text/html, application/xhtml+xml, */*',
    'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
    'Connection': 'keep-alive',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0'
    }):
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    header = []
    for key, value in head.items():
        elem = (key, value)
        header.append(elem)
    opener.addheaders = header
    return opener

# ------ 获取网页源代码 ---
# url 网页链接地址
def getHtml(url):
    # print('url='+url)
    oper = makeOpener()
    if oper is not None:
        page = oper.open(url)
        #print ('-----oper----')
    else:
        req=urllib.request.Request(url)
        # 爬虫伪装浏览器
        req.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64; rv:57.0) Gecko/20100101 Firefox/57.0')
        page = urllib.request.urlopen(req)
    html = page.read()
    if collectHtmlEnabled: #是否采集html
       with open('html.txt', 'wb') as f:
           f.write(html)  # 采集到本地文件，来分析
    # ------ 修改html对象内的字符编码为UTF-8 ------
    if chardetSupport:
        cdt = chardet.detect(html)
        charset = cdt['encoding'] #用chardet进行内容分析
        print(charset)
    else:
       charset = 'utf8'
    try:
       result = html.decode(charset)
    except:
       result = html.decode('gbk')
    return result

# ------ 固定长度的随机字符串 ---
def random_str(randomlength=8,chars='AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'):
    str = ''
    length = len(chars) - 1
    random = Random()
    for i in range(randomlength):
        str+=chars[random.randint(0, length)]
    return str

# ------ 根据图片url下载图片 ------
# folderPath 定义图片存放的目录 imgUrl 一个图片的链接地址 index 索引，表示第几个图片
def downloadImg(folderPath, imgUrl, index):
    # ------ 异常处理 ------
    try:
        imgeNameFromUrl = os.path.basename(imgUrl)
        #print(imgUrl)
        imgContent = (urllib.request.urlopen(imgUrl)).read()
        
    except urllib.error.URLError as e:
        if printLogEnabled :
            print('URL error: '+imgUrl) 
            #print('URL Error 当前图片无法下载')
        return False
#    except urllib.error.HTTPError as e:
#        if printLogEnabled : print  ('【HTTP错误】当前图片下载异常')
#        return False
#    finally:
    else:
        imgeNameFromUrl = os.path.basename(imgUrl)
        if printLogEnabled : print ('正在下载第'+str(index+1)+'张图片，图片地址:'+str(imgUrl))
        # ------ IO处理 ------
        isExists=os.path.exists(folderPath)
        if not isExists:  # 目录不存在，则创建
             os.makedirs( folderPath )
             #print  ('创建目录')
        # 图片名命名规则，随机字符串
        imgName = imgeNameFromUrl
        #if printLogEnabled : print (imgName)
        #if len(imgeNameFromUrl) < 8:
        #    imgName = random_str(4) + random_str(1,'123456789') + random_str(2,'0123456789')+"_" + imgeNameFromUrl
        #filename= folderPath + "\\"+str(imgName)+".jpg"
        filename= folderPath + "\\"+str(index)+".jpg"
        try:
             with  open(filename, 'wb') as f:
                 f.write(imgContent)  # 写入本地磁盘
             # if printLogEnabled : print ('下载完成第'+str(index+1)+'张图片')
        except :
            return False
        return True

# ------ 批量下载图片 ------
# folderPath 定义图片存放的目录 imgList 多个图片的链接地址
def downloadImgList(folderPath, imgList):
   index = 0
   # print ('poolSupport='+str(poolSupport))
   if not poolSupport:
      print ('多线程模式')
      # ------ 多线程编程 ------
      threads = []
      for imgUrl in imgList:
          # if printLogEnabled : print ('准备下载第'+str(index+1)+'张图片')
          threads.append(threading.Thread(target=downloadImg,args=(folderPath,imgUrl,index,)))
          index += 1
      for t in threads:
          t.setDaemon(True)
          t.start()
      t.join() #父线程，等待所有线程结束
      if len(imgList) >0 : print ('下载结束，存放图片目录：' + str(folderPath))
   else:
      print ('线程池模式')
       # ------ 线程池编程 ------
      futures = []
      # 创建一个最大可容纳N个task的线程池  thePoolSize 为 全局变量
      with concurrent.futures.ThreadPoolExecutor(max_workers=thePoolSize)  as pool: 
        for imgUrl in imgList:
          # if printLogEnabled : print ('准备下载第'+str(index+1)+'张图片')
          #print(imgUrl)
          futures.append(pool.submit(downloadImg, folderPath, imgUrl, index))
          index += 1
        result = concurrent.futures.wait(futures, timeout=None, return_when='ALL_COMPLETED')
        suc = 0
        for f in result.done:
            if f.result():  suc +=1
        print('下载结束，总数：'+str(len(imgList))+'，成功数：'+str(suc)+'，存放图片目录：' + str(folderPath))



def downloadImgFromXXX(folderPath='test', url='https://ck101.com/thread-4545220-1-1.html'):
    html = getHtml(url)
    #print (html)
    soup = bs(html, 'html.parser')
    print ('Roger Test : ')
    print (soup.title)
    #print (soup.contents)
    #print (soup.select('.zoom'))
    items = soup.select('.zoom')
    
    imgList = []
    #for key in imgKeyList:
    #    imgList.append('http://img.hb.aicdn.com/' + key)
    myname = 'xxx.log'
              
    for i in items:
        print (i.get('file'))
        imgList.append(i.get('file'))        
     
    
    print ('找到图片个数：' + str(len(items)))
    # 下载图片 call downloadImgList()
    if len(items) >0 :         
        downloadImgList(folderPath, imgList)


# ______________________ main() _________________________________
if __name__ == '__main__':
    now = datetime.datetime.now().strftime('%Y-%m-%d %H-%M-%S')
    #call downloadImgFromXXX()
    downloadImgFromXXX('test\\'+now, 'https://ck101.com/thread-4545220-1-1.html')

    