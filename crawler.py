# coding:utf8
#!/usr/bin/python

from bs4 import BeautifulSoup
import re
import os
import os.path
import time
import sys
import thread
import getopt
import urllib2


global HAVE_SAVED_AMOUNT
global MAX_SAVED_AMOUNT
global SAVE_PATH


def timer(no, interval):
    cnt = 0
    while cnt < 10:
        print 'Thread:(%d) Time:%s\n' % (no, time.ctime())
        time.sleep(interval)
        cnt += 1
    thread.exit_thread()


def test():  # Use thread.start_new_thread() to create 2 new threads
    thread1 = timer(1, 1)
    thread2 = timer(2, 2)
    thread1.start()
    thread2.start()
    # thread.start_new_thread(thread1)
    # thread.start_new_thread(thread2)


def usage():
    print("Usage:")
    print("-h for help")
    print("-i , the number of thread")
    print("-o , path for saving images")
    print("-l , max number of crawing images , default is not limited")


def save_image(url):
    global HAVE_SAVED_AMOUNT
    global MAX_SAVED_AMOUNT
    global SAVE_PATH

    if MAX_SAVED_AMOUNT < 0 or HAVE_SAVED_AMOUNT < MAX_SAVED_AMOUNT:
        content2 = urllib2.urlopen(url).read()
        with open(SAVE_PATH + '/' + url[-30:], 'wb') as code:
            code.write(content2)
        HAVE_SAVED_AMOUNT += 1
    else:
        print('have saved %s images , this will exit' % HAVE_SAVED_AMOUNT)
        sys.exit()


if __name__ == '__main__':
    global HAVE_SAVED_AMOUNT
    global MAX_SAVED_AMOUNT
    global SAVE_PATH
    HAVE_SAVED_AMOUNT = 0
    MAX_SAVED_AMOUNT = -1
    opts, args = getopt.getopt(sys.argv[1:], "hl:n:o:")
    SAVE_PATH = "pics"
    concurrent = 10
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
    page = urllib2.urlopen('http://www.22mm.cc/mm/qingliang/PiaeaJCJCCJaiHdmJ.html')
    soup = BeautifulSoup(page)
    my_girl = soup.find_all('div', id='box-inner')
    image_url = ''
    for girl in my_girl:
        imgs = girl.findAll("script")
        for img in imgs:
            contains = str(img).find('http')
            if contains >= 0:
                print(img)
                image_url = str(img)
            else:
                continue
    urls = re.findall('http://[_a-zA-Z0-9./-]+', image_url, re.I)
    for i in urls:
        image_url = i

    image_url = image_url.replace('big', 'pic')
    print(image_url)  # this image_url is end url
    if not os.path.exists(SAVE_PATH):
        os.makedirs(SAVE_PATH)
    save_image(image_url)
