#import sys

from bs4 import BeautifulSoup
import urllib.request


def read_webpage(url):

    try:
        request=urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}) #The assembled request
        response = urllib.request.urlopen(request)
        page = response.read()
        index = url.rfind('/')
        # webpage = urllib.request.urlopen(url,headers = hdr)
    except:
        # print("ERROR READING PAGE")
        return None, None

    
    return page, index


def html_parser(page):
    if page:
        soup = BeautifulSoup(page, 'html.parser')
        return soup
    else:
        return None
