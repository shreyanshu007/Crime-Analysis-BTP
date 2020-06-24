#!/home/2016CSB1059/project_env/bin/python
import urllib.request
import websiteparser as wp
import textprocessing as tp
import newspaper
import json
import InsertionIntodatabase as db
import time
import datetime


TOTAL_TIME = 23*60*60
URL = "https://www.hindustantimes.com/"
initial_time = time.time()

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
def extract_details(title, text, date, url, location):

    date = date.strftime("%Y-%m-%dT%H:%M:%S+05:30")
    if not db.IsUrlExists(url):
    #     # print(date)
        db.InsertIntoDatabase(date, url, title, text, location)
        print("Data Added")


# adding the given url to the database if the url is new and further depth allowed.
# further depth allowed means that how deep user asked for reading urls for collecting article.
def hindustanTimesNews(url, depth, CITY_LIST):
    # calling for given URL.
    # checking if further depth allowed.
    final_time = time.time()
    if depth > 0 and (final_time - initial_time) < TOTAL_TIME:
        # is this url already present or not
        if not db.IsUrlExists(url):
            # reading url
            pgsrc, index = wp.read_webpage(url)
            # if url is opened and read
            if pgsrc:
                url_soup = wp.html_parser(pgsrc)
                # extracting the meta data of the url to check whether it is article or non-article url
                tag = url_soup.find('meta', {'property': 'og:type'})
                
                if tag and tag.get('content') == 'article':
                    print("Article")
                    try:
                        # if the url is article type then extract required details and do further processing.
                        article = newspaper.Article(url)
                        article.download()
                        article.parse()
                        location = url_soup.find('meta', {'name': 'section'})
                        location = location.get('content').split()[0].split('-')[0]
                        if any(item.lower() in location.lower() for item in CITY_LIST):
                            extract_details(article.title, article.text, article.publish_date, article.url, location)

                    except Exception as e:
                        print("Exception occurred: ", e)

                else:
                    print("Non Article")

                # extract all anchor tags in this webpage and then send each url for further procesing .
                returned_url_list = url_soup.find_all('a')
                # print(returned_url_list)
                for return_url in returned_url_list:

                    link = return_url.get('href')
                    if link and link != URL:
                        # checking if the url is complete or not i.e. starting with http ot not.
                        if 'http' not in link:
                            link = return_link(URL, link)
                            # addition of all the urls present in this web page
                            if any(item in link for item in CITY_LIST):
                                hindustanTimesNews(link, depth-1, CITY_LIST)

                        elif 'hindustantimes.com' in link:
                            # addition of all the urls present in this web page
                            if any(item in link for item in CITY_LIST):
                                hindustanTimesNews(link, depth-1, CITY_LIST)
                    else:
                        pass
                        #print("NO LINK")
            else:
                pass                
               # print("ERROR READING PAGE")
        else:
            pass
            #print("ALREADY PRESENT")
    else:
        pass
        # print(depth)


# starting point of the crawler process.
# takes input as the url of the site and crawling depth.
def HindustanTimesNewsSiteCrawler(url, depth, CITY_LIST):
    print("Opening the Website: ", url)
    # reading given url page
    pgsrc, index = wp.read_webpage(url)

    # if source page read is not None
    if pgsrc:

        # parsing the page
        soup = wp.html_parser(pgsrc)

        # read all anchor tags
        a_tags = soup.find_all('a')
        # print(a_tags)
        for tag in a_tags:

            link = tag.get('href')
            if 'http' not in link:
                link = return_link(url, link)

            hindustanTimesNews(link, depth, CITY_LIST)
    else:
        print("can't read")


# HindustanTimesNewsSiteCrawler("https://www.hindustantimes.com/topic/crime", 10)
# hindustanTimesNews('https://www.hindustantimes.com/india-news/soldiers-killed-on-border-without-war-mohan-bhagwat-s-stinker-to-centre/story-9PWXwsWIN2RUA5aV0PuHGL.html', 2, 5)

if __name__ == '__main__':

    CITY_LIST = ['delhi', 'bangalore', 'mumbai', 'chennai', 'lucknow', 'chandigarh', 'hyderabad', 'kolkata']
    hindustanTimesNews('https://www.hindustantimes.com/mumbai-news/rain-supreme-in-mumbai-set-to-break-record/story-ubS5ldu0c14yhyZuHOCZOJ.html', 5, CITY_LIST)
