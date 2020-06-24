#!/home/2016CSB1059/project_env/bin/python
import urllib.request
import websiteparser as wp
import textprocessing as tp
import newspaper
from PIL import Image
import json
import InsertionIntodatabase as db
import time

TOTAL_TIME = 23*60*60
initial_time = time.time()
URL = "https://www.news18.com/"

# takes two urls as input combines them to complete the incomplete url.
# url1 = http://www.timesofindia.com/ or similar
# url2 = /city/chandigarh
# output = url1 + url2 = http://www.timesofindia.com/city/chandigarh
# so that our crawler can visit the proper website.
def return_link(url1, url2):
    index = url1.rfind('/')
    if url2[0] == '/' and url1[-1] == '/':
        return url1[0:index] + url2
    elif (url2[0] == '/' and url1[-1] != '/') or (url2[0] != '/' and url1[-1] == '/'):
        return url1 + url2
    else:
        return url1 + "/" + url2


# takes the parsed source page of the website and extracts the relevant details from the website.
# eg. title, date, title and content of the news.
def extractToiNews(title, text, date, url, location):

    if not db.IsUrlExists(url):
        # print(date)
        db.InsertIntoDatabase(date, url, title, text, location)
        print("data added")


# reads the urls of website and if a news article it stores the new details in storage.
def news18(url, depth, CITY_LIST):
    # calling for given URL.
    # checking if further depth allowed.
    final_time = time.time()
    if depth > 0 and (final_time - initial_time) < TOTAL_TIME:
        # is this url already present or not
        if not db.IsUrlExists(url):
        # if not db.IsUrlExists(url):
            # reading url
            pgsrc, index = wp.read_webpage(url)
            # if url is opened and read
            if pgsrc:
                url_soup = wp.html_parser(pgsrc)
                # extracting the meta data of the url to check whether it is article or non-article url
                url_type = url_soup.find('meta', {'property': 'og:type'})
                # if the url is article type.
                if url_type and url_type.get('content').lower() in ['article', 'story']:
                    # if the url is article type then extract required details and do further processing.
                    try:
                        article = newspaper.Article(url)
                        article.download()
                        article.parse()

                        date_tags = url_soup.find_all('script', {'type': 'application/ld+json'})
                        for date_tag in date_tags:
                            contentDict = eval(date_tag.get_text())
                            if 'datePublished' in contentDict.keys():
                                articleDate = contentDict['datePublished']
                                break

                        location = None
                        for city in CITY_LIST:
                            if city in article.url:
                                location = city
                                break

                        if location:
                            extractToiNews(article.title, article.text, articleDate, article.url, location)

                    except Exception as e:
                        print(str(e))

                # extract all anchor tags in this webpage and then send ecah url for further procesing .
                returned_url_list = url_soup.find_all('a')

                for return_url in returned_url_list:

                    link = return_url.get('href')
                    if link and link != URL:
                        # checking if the url is complete or not i.e. starting with http ot not.
                        if 'http' not in link:
                            link = return_link(URL, link)
                            # addition of all the urls present in this web page
                            if any(item in link for item in CITY_LIST):
                                news18(link, depth-1, CITY_LIST)

                        elif 'news18.com' in link:
                            # addition of all the urls present in this web page
                            if any(item in link for item in CITY_LIST):
                                news18(link, depth-1, CITY_LIST)

                        


# starting point of the crawler process.
# takes input as the url of the site and crawling depth.
def News18SiteCrawler(url, depth, CITY_LIST):
    print("Opening the Website: ", url)
    
    # reading given url page
    pgsrc, index = wp.read_webpage(url)

    # if source page read is not None
    if pgsrc:

        # parsing the page
        soup = wp.html_parser(pgsrc)

        # read all anchor tags
        a_tags = soup.find_all('a')

        for tag in a_tags:
            
            if tag:
                link = tag.get('href')
                if link and 'http' not in link:
                    link = return_link(url, link)
    
                news18(link, depth, CITY_LIST)


# function to check these operations working or not.....
def download_url(url):
    article = newspaper.Article(url)
    article.download()
    article.parse()
    print(article.text)

# download_url("https://timesofindia.indiatimes.com/blogs/erratica/statue-mev-jayate-in-government-by-slogan-only-tall-tales-shall-triumph-f0-9f-98-9c/?utm_source=Popup&utm_medium=Old&utm_campaign=TOIHP")
# News_site_toi("https://www.news18.com/newstopics/crime.html", 10)
# news18("https://www.news18.com/news/india/indian-prisoner-hamid-nihal-ansari-released-by-pakistan-after-6-years-of-imprisonment-1975953.html?ref=hp_top_pos_5", 1)

if __name__ == '__main__':

    CITY_LIST = ['delhi', 'bangalore', 'mumbai', 'chennai', 'lucknow', 'chandigarh', 'hyderabad', 'kolkata']
    news18('https://www.news18.com/news/india/robert-vadra-moves-delhi-court-to-travel-spain-other-european-countries-2302563.html', 5, CITY_LIST)
