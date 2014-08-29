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
import hashlib
from time import sleep
from Queue import Queue
from threading import Thread

global HAVE_SAVED_AMOUNT
global MAX_SAVED_AMOUNT
global SAVE_PATH

# q是任务队列
queue = Queue()

# 伪装浏览器头
HEADER = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.94 Safari/537.36'}
# 日志配置，全局的, logging setting start ,just like sl4j
logger = logging.getLogger()

# 帮助-h显示
def usage():
    print('''Usage:
    -h for help
    -n , the number of thread
    -o , path for saving images
    -l , max number of crawing images , default is not limited''')


# 这个是工作进程，负责不断从队列取数据并处理
class working(Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self, num, interval):
        Thread.__init__(self)
        self.thread_num = num
        self.interval = interval
        self.thread_stop = False

    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            url = queue.get()
            if url != '':
                save_image(url)
            queue.task_done()
            if self.interval > 0:
                sleep(self.interval)

    def stop(self):
        self.thread_stop = True


# 保存图片url到本地
def save_image(url):
    global HAVE_SAVED_AMOUNT
    global MAX_SAVED_AMOUNT
    global SAVE_PATH

    try:
        if MAX_SAVED_AMOUNT < 0 or HAVE_SAVED_AMOUNT < MAX_SAVED_AMOUNT:
            request = urllib2.Request(url, None, HEADER)
            content2 = urllib2.urlopen(request).read()
            name = hashlib.md5(url).hexdigest().lower()
            name = name + url[-4:]
            if os.path.exists(SAVE_PATH + '/' + name):
                logger.debug("[image exists][%s]" % name)
                return
            else:
                with open(SAVE_PATH + '/' + name, 'wb') as code:
                    code.write(content2)
                HAVE_SAVED_AMOUNT += 1
                logger.info('[Saved][%s]' % name)
        else:
            logger.info('[Error] have saved %s images , this will exit' % HAVE_SAVED_AMOUNT)
            sys.exit()
    except Exception, ex:
        print Exception, ":", ex


# 初始化logger
def iniLogger():
    fileHandler = logging.FileHandler('log.txt')  # 文件日志
    consoleHandler = logging.StreamHandler()  # 控制台日志
    consoleHandler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(asctime)s][%(threadName)-12s][%(levelname)-6s][Line:%(lineno)d] %(message)s')
    fileHandler.setFormatter(formatter)
    consoleHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    logger.setLevel(logging.NOTSET)


# 解析出图片url，将图片url放入queue
def parse_image_url(url):
    try:
        # url = 'http://www.22mm.cc/mm/qingliang/PiaedCCeHHdadHaii.html'
        request = urllib2.Request(url, None, HEADER)
        page = urllib2.urlopen(request)
        soup = BeautifulSoup(page)

        page = soup.find("div", "ShowPage").find("strong");
        pageCount = re.findall('/[\d]+', str(page), re.I)
        pageCount = int(pageCount[0].replace("/", ''))
        logging.info('[Parse]find page count is %s ' % pageCount)

        get_image_url_from_soup(soup)

        pageNo = 1
        while pageNo < pageCount:
            pageNo += 1
            new_url = url.replace('.html', '-%s.html' % pageNo)
            parse_image(new_url)
    except Exception, ex:
        print Exception, ":", ex


def get_all():
    url = 'http://www.22mm.cc/mm/qingliang/index.html'
    request = urllib2.Request(url, None, HEADER)
    page = urllib2.urlopen(request)
    soup = BeautifulSoup(page)

    images_div = soup.find_all("div", "c_inner")

    for p in images_div:
        p2 = p.find_all('a')
        for item in p2:
            next_url = 'http://www.22mm.cc' + item.get('href')
            logger.info(next_url + item.get('title'))
            parse_image_url(next_url)

    show_pages = soup.find_all('div', 'ShowPage')
    for show_page in show_pages:
        logger.info(show_page)


def get_image_url_from_soup(soup):
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
    # 有一个算是bug，在script里面有多个arrayImage[0],会把之前的覆盖掉，导致本地很多重复的url，但存在有页面确实有多个图片显示的问题
    for i in urls:
        image_url = i.replace('big', 'pic')  # this image_url is end url
        logging.info('[Parse] put url into queue, %s ' % image_url)
        queue.put(image_url)


def parse_image(url):
    try:
        request = urllib2.Request(url, None, HEADER)
        page = urllib2.urlopen(request)
        soup = BeautifulSoup(page)
        get_image_url_from_soup(soup)
    except Exception, ex:
        print Exception, ":", ex


if __name__ == '__main__':
    global HAVE_SAVED_AMOUNT
    global MAX_SAVED_AMOUNT
    global SAVE_PATH

    HAVE_SAVED_AMOUNT = 0
    MAX_SAVED_AMOUNT = -1
    opts, args = getopt.getopt(sys.argv[1:], "hl:n:o:")
    SAVE_PATH = "pics"  # 保存路径，默认为当前目录下的pics
    concurrent = 10  # concurrent是并发线程总数
    MAX_SAVED_AMOUNT = -1
    iniLogger()

    for op, value in opts:
        if op == "-n":
            concurrent = int(value)
        elif op == "-o":
            SAVE_PATH = value
        elif op == "-l":
            MAX_SAVED_AMOUNT = int(value)
            if int(value) < 0:
                logger.error("illegal -l value [%s]", value)
                sys.exit()
        elif op == "-h":
            usage()
            sys.exit()

    logger.debug('crawler program start')

    # fork concurrent个线程等待队列
    for i in range(concurrent):
        t = working(i, 1)
        t.setName("SaveThread-%d" % i)
        t.setDaemon(True)
        t.start()

    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    HAVE_SAVED_AMOUNT = sum([len(files) for root, dirs, files in os.walk(SAVE_PATH)])
    if MAX_SAVED_AMOUNT < 0 or HAVE_SAVED_AMOUNT < MAX_SAVED_AMOUNT:
        get_all()
        queue.join()  # 等待所有JOBS完成
    else:
        logger.info('Have saved ' + str(HAVE_SAVED_AMOUNT) + ' files , and Max is ' + str(MAX_SAVED_AMOUNT))