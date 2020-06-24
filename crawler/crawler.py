#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python

# importing the threading module 
import threading 
import pymysql
import toicrawler
import hindustantimescrawler
import indiaTodayCrawler
import ndtvCrawler
import news18Crawler
import thehinducrawler

CITY_LIST = ['delhi', 'bangalore', 'mumbai', 'chennai', 'lucknow', 'chandigarh', 'hyderabad', 'kolkata']


def ToiCrawler(url=""): 
	""" 
	function to call toiCrawler
	"""
	toicrawler.ToiNewsSiteCrawler(url, 10, CITY_LIST)


def HindustanTimesCrawler(url=""): 
	""" 
	function to call hindustantimescrawler
	"""
	hindustantimescrawler.HindustanTimesNewsSiteCrawler(url, 10, CITY_LIST)


def IndiaTodayCrawler(url=""): 
	""" 
	function to call IndiaTodayCrawler
	"""
	indiaTodayCrawler.IndiaTodayNewsSiteCrawler(url, 10, CITY_LIST)


def NDTVCrawler(url=""): 
	""" 
	function to call NDTVCrawler
	"""
	ndtvCrawler.NdtvTvNewsSiteCrawler(url, 10, CITY_LIST)


def News18Crawler(url=""): 
	""" 
	function to call NDTVCrawler
	"""
	news18Crawler.News18SiteCrawler(url, 10, CITY_LIST)


def TheHinduCrawler(url=""): 
	""" 
	function to call NDTVCrawler
	"""
	thehinducrawler.TheHinduNewsSiteCrawler(url, 10, CITY_LIST)


if __name__ == "__main__": 
	# creating thread 
	t1 = threading.Thread(target=ToiCrawler, kwargs={'url':'https://timesofindia.indiatimes.com/city/delhi?cfmid=2000000'}) 
	t2 = threading.Thread(target=HindustanTimesCrawler, kwargs={'url':'https://www.hindustantimes.com/delhi-news/'}) 
	t3 = threading.Thread(target=IndiaTodayCrawler, kwargs={'url':'https://www.indiatoday.in/india'}) 
	t4 = threading.Thread(target=NDTVCrawler, kwargs={'url':'https://www.ndtv.com/delhi-news'}) 
	t5 = threading.Thread(target=News18Crawler, kwargs={'url':'https://www.news18.com/india/'}) 
	t6 = threading.Thread(target=TheHinduCrawler, kwargs={'url':'https://www.thehindu.com/news/cities/Delhi/'}) 


	# starting threads
	t1.start()  
	t2.start() 
	t3.start() 
	t4.start() 
	t5.start() 
	t6.start() 

	# wait until threads to completely executed 
	t1.join() 
	t2.join() 
	t3.join() 
	t4.join() 
	t5.join() 
	t6.join() 