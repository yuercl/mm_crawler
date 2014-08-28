# -*-encoding:utf-8-*-
#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import os
import os.path
import sys
import getopt
import urllib2
import logging
from Queue import Queue
from time import sleep
from threading import Thread

global HAVE_SAVED_AMOUNT
global MAX_SAVED_AMOUNT
global SAVE_PATH

# q是任务队列
queue = Queue()

# 伪装浏览器头
HEADER = {'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
# 日志配置，全局的, logging setting start ,just like sl4j
logger = logging.getLogger()

# 帮助-h显示
def usage():
    print("Usage:")
    print("-h for help")
    print("-i , the number of thread")
    print("-o , path for saving images")
    print("-l , max number of crawing images , default is not limited")


# 这个是工作进程，负责不断从队列取数据并处理
def working():
    while True:
        url = queue.get()
        save_image(url)
        sleep(1)
        queue.task_done()


# 保存图片url到本地
def save_image(url):
    global HAVE_SAVED_AMOUNT
    global MAX_SAVED_AMOUNT
    global SAVE_PATH

    logger.info('[Save] start get image %s ' % url)

    if MAX_SAVED_AMOUNT < 0 or HAVE_SAVED_AMOUNT < MAX_SAVED_AMOUNT:
        request = urllib2.Request(url, None, HEADER)
        content2 = urllib2.urlopen(request).read()
        with open(SAVE_PATH + '/' + url[-30:], 'wb') as code:
            code.write(content2)
        HAVE_SAVED_AMOUNT += 1
    else:
        logger.info('[Save] have saved %s images , this will exit' % HAVE_SAVED_AMOUNT)
        sys.exit()


# 初始化logger
def iniLogger():
    fileHandler = logging.FileHandler('log.txt')  # 文件日志
    consoleHandler = logging.StreamHandler()  # 控制台日志
    consoleHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)-5s] %(message)s')
    fileHandler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.NOTSET)


# 解析出图片url，将图片url放入queue
def parse_image_url():
    request = urllib2.Request('http://www.22mm.cc/mm/qingliang/PiaeaJCJCCJaiHdmJ.html', None, HEADER)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)

    page = soup.find("div", "ShowPage").find("strong");
    pageNum = re.findall('/[\d]+', str(page), re.I)
    pageNum = pageNum[0].replace("/", '')
    logging.info('[Parse]find page count is %s ' % pageNum)

    my_girl = soup.find_all('div', id='box-inner')
    image_url = ''
    for girl in my_girl:
        imgs = girl.findAll("script")
        for img in imgs:
            contains = str(img).find('http')
            if contains >= 0:
                image_url = str(img)
            else:
                continue
    urls = re.findall('http://[_a-zA-Z0-9./-]+', image_url, re.I)
    for i in urls:
        image_url = i

    image_url = image_url.replace('big', 'pic')  # this image_url is end url

    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    logging.info('[Parse] put url into queue, %s ' % image_url)
    queue.put(image_url)


if __name__ == '__main__':
    global HAVE_SAVED_AMOUNT
    global MAX_SAVED_AMOUNT
    global SAVE_PATH

    iniLogger()
    logger.debug('crawler program start')

    HAVE_SAVED_AMOUNT = 0
    MAX_SAVED_AMOUNT = -1
    opts, args = getopt.getopt(sys.argv[1:], "hl:n:o:")
    SAVE_PATH = "pics"  # 保存路径，默认为当前目录下的pics
    concurrent = 10  # concurrent是并发线程总数
    limit = -1

    for op, value in opts:
        if op == "-n":
            concurrent = value
            print(value)
        elif op == "-o":
            SAVE_PATH = value
        elif op == "-l":
            limit = value
            if int(limit) < 0:
                print("illegal -l value [%s]", limit)
                sys.exit()
        elif op == "-h":
            usage()
            sys.exit()

    # fork NUM个线程等待队列
    for i in range(concurrent):
        t = Thread(target=working)
        t.setName("thread %d " % i)
        t.setDaemon(True)
        t.start()

    parse_image_url()
    # 等待所有JOBS完成
    queue.join()