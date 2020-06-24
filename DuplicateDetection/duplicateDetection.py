#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python

# modules to import
import pymysql
from nltk.tag import StanfordNERTagger
from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize
import nltk
from datetime import datetime, timedelta
from dateutil.rrule import rrule, MONTHLY
import sys
import os
f = os.path.dirname(os.path.abspath(__file__))
ind = f.rfind('/')
sys.path.append(f[:ind+1])
import CrimeClassification.MainCrimeClassifier as fileCrimeClassify
from LocationExtraction import locationExtraction as le
from DuplicateDetection.simhash import simhash
from DuplicateDetection.older_changes import similarity_score
import DuplicateDetection.fetch_duplicate_data as fdd

#### stanford tagger classifier load
st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') # doctest: +SKIP

# For debugging and dataset checking --------
# GLOBAL_COUNT = 0
# LOCAL_COUNT  = 0
# file = open('check.log', 'w')
# -------------------------------------------


'''
	Class for Duplicate Detection
	A single instance stores details of an article
	See contructor for object initialisation
'''
class DuplicateDetection(object):

	news_id = None
	current_news_text = None
	news_date = None
	news_published_location = None
	crime_type = None
	person_entities = None
	location_entities = None
	organization_entities = None
	entities = []
	tagger = None
	word_tokenizer = None
	article_set = None

	def __init__(self, news_id, text, date, news_published_location, tagger, word_tokenizer):
		'''
			constructor:
			Varibles - DB column of NewsArticles(Refer DB for details)
			news_id - NewsArticleID
			text - NewsArticleText
			date - NewsArticleDate
			news_published_location - Location
			tagger - tagger to tag text(Stanford used here, pass stanford tagger)
			word_tokenizer - tokenizer to tokenize sentences
		'''
		self.news_id = news_id
		self.current_news_text = text
		self.news_date = date
		self.news_published_location = news_published_location
		self.tagger = tagger
		self.word_tokenizer = word_tokenizer
		self.person_entities = []
		self.location_entities = []
		self.organization_entities = []

		# initialize entities and crime type
		self.crimeType()
		self.extractSelfEntities()

	def returnCurrentNewsText(self):
		return self.current_news_text

	def crimeType(self):
		''' To find crime type of article instance '''
		self.crime_type = fileCrimeClassify.extractCrimeWord(self.current_news_text, returnOnlyLabels=True)

	def extractSelfEntities(self):
		'''
			Extracts entities for self article:
			stores in self.entities
				self.location_entities
				self.organization_entities
				self.person_entities
		'''
		self.entities = le.nltkTagger(self.current_news_text)
		for entity, tag in self.entities.items():
			if tag in ['LOCATION','GPE']:
				self.location_entities.append(entity)
			elif tag == 'PERSON':
				self.person_entities.append(entity)
			elif tag == 'ORGANIZATION':
				self.organization_entities.append(entity)

		self.location_entities = list(set(self.location_entities))
		self.person_entities = list(set(self.person_entities))
		self.organization_entities = list(set(self.organization_entities))
		# return self.location_entities, self.person_entities, self.organization_entities


	def extractTextEntities(self, text):
		'''
			Extracts entities for given text
			input: text - text
			output: location_entities, person_entitie, organization_entities
		'''
		entities = le.nltkTagger(text)
		location_entities = []
		person_entities = []
		organization_entities = []
		# print(entities)
		for entity, tag in entities.items():
			# print(entity)
			if tag in ['LOCATION','GPE']:
				location_entities.append(entity)
			elif tag == 'PERSON':
				person_entities.append(entity)
			elif tag == 'ORGANIZATION':
				organization_entities.append(entity)

		location_entities = list(set(location_entities))
		person_entities = list(set(person_entities))
		organization_entities = list(set(organization_entities))
		return location_entities, person_entities, organization_entities

	def returnmatchescount(self, list1, list2):
		### Returns length of common elements in the list1 and list2
		### input: list1/2
		### length of common elements of list1/2
		total = []
		small = large = None
		list1 = [l.lower() for l in list1]
		list2 = [l.lower() for l in list2]
		self.filter_list(list1)
		self.filter_list(list2)
		#print(len(list1), len(list2))
		if len(list1) < len(list2):
			small = list1
			large = list2
		else:
			small = list2
			large = list1

		for item in small:
			if item in large:
				total.append(item)
				continue
			for it in large:
				if item in it or it in item:
					total.append(item)
					break
		return len(set(total))
		for item1 in small:
			for item2 in large:
				dis = 0
				if len(item1) < len(item2):
					dis = simhash.hamming_distance(item1, item2)
				else:
					dis = simhash.hamming_distance(item2, item1)
				#print(item1, item2, dis)
				if dis == 0:
					total.append(item1)
					break
				
					
		return len(set(total))

	def return_line(self, p1, p2):
		### given two points p1 and p2 returns line joining them
		### output: a,b,c of line ax + by + c = 0
		m = (p2[1] - p1[1])/(p2[0] - p1[0])
		return m, -1, p1[1] - m*p1[0]

	def isArticleSimilar(self, article_entities, article_text):
		### return if article is similar with the article stored in the class
		'''
			input: article_entities, article text
			output: True/False
		'''
		c1 = self.returnmatchescount(self.location_entities + self.person_entities + self.crime_type, article_entities)
		#c2 = self.returnmatchescount(article_entities, self.person_entities + self.location_entities + self.crime_type)
		#print(article_entities)
		#print(self.location_entities + self.person_entities + self.crime_type)
		
		common_length = c1
		#print(common_length)
		l1 = len(self.location_entities + self.person_entities + self.crime_type)
		l2 = len(article_entities)
		min_len = min(l1,l2)
		sim_value = similarity_score(self.current_news_text, article_text)
		if min_len == 0:
			if sim_value >= 0.7:
				return True
			return False
		val = common_length/min(l1,l2)
		#print(val, sim_value)
		a,b,c = self.return_line((0.6,0.0),(0.0,1.0))
		if (val + sim_value) >= 0.7:
			return True

		return False

	def fetchArticlesForComparison(self):
		'''
			Fetches all articles for comparison from DB.
			IMP*: YOu can change no. of days for article comparison in predecessor_date
		'''
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		curr_date = self.news_date
		successor_date = curr_date
		predecessor_date = curr_date + timedelta(days=-14)		# Can change no. of days.
		result = None
		#print(predecessor_date, self.news_date, successor_date)
		sql = "SELECT * FROM NewsArticles WHERE NewsArticleDate BETWEEN %s AND %s AND Location = %s AND NewsArticleID <> %s AND (DuplicateReferenceId = -1 OR DuplicateReferenceId = -2)"
		# sql = "SELECT * FROM NewsArticles LIMIT 2"

		try:
			db = connection.cursor()
			result = db.execute(sql,(predecessor_date, successor_date, self.news_published_location, self.news_id))
			# result = db.execute(sql)
			result = db.fetchall()
			connection.commit()

		except Exception as e:
			connection.rollback()

		finally:
			db.close()
			connection.close()

		return result

	def checkSimilarity(self):
		'''
			Only returning the first match of the duplicate article.
			List can be used for complete solution network.
			output: Dup. Art. ID / None
			IMP*: Run only after you have initialised instance of the class.
		'''
		articles = self.fetchArticlesForComparison()
		for article in articles:
			news_text = article[1] + " " + article[2]
			crime_type = fileCrimeClassify.extractCrimeWord(news_text, returnOnlyLabels=True)
			l, p, o = self.extractTextEntities(news_text)
			ans = self.isArticleSimilar(crime_type + l + p +o, article[1] + " " + article[2])
			if ans:
				return article[0]

		return None


# function to fetch newsarticles from database for checking.
def transfer(articleID=None):
	### fetches article from database using sql query
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT * FROM NewsArticles WHERE NewsType = 'crime' LIMIT 10000"
	if articleID:
		sql = "SELECT * FROM NewsArticles WHERE NewsArticleID = %s"
	
	text = None
	try:
		with connection:
			db = connection.cursor()
			if articleID:
				result = db.execute(sql,(articleID))
				result = db.fetchall()
				text = result[0]
			# result = 
			else:
				db.execute(sql,)
				text = db.fetchall()
			# text = result[0][2] + " " + result[0][3]
			connection.commit()
		

	except Exception as e:
		# print("exception ", e)
		connection.rollback()
	finally:
		# print("finally")
		db.close()
		connection.close()

	return text

if __name__ == '__main__':
	
	from random import randrange as rr
	import random
	list1 = [14399,34409,43171,63187,63655,63681,64122,64211,64734,64398,65948,65997,66077,66308,66916,68137,67595,68392,68390,68393]
	list2 = [3,4,12,35,40,49,67,68,74,81,95,117,119,133,139,147,148,169,172,178]
	sim = fdd.similar_data()
	diff = fdd.different_data()
	total = diff + sim
	random.shuffle(total)
	table = [[0,0], [0,0]]
	same = 0
	for i in range(800):
		print(i)
		num1 = rr(1,40,1)
		num2 = rr(1,40,1)
		if num1 == num2:
			same += 1
			continue
		#print(num1, num2)
		#print(total[num1])
		#print(total[num2])
		t1 = total[num1][1] + " " + total[num1][2]
		t2 = total[num2][1] + " " + total[num2][2]
		dd = DuplicateDetection(total[num1][0], t1, None, None, st, word_tokenize)
		dd.extractSelfEntities()
		l,p,o = dd.extractTextEntities(t2)
		crime_type = fileCrimeClassify.extractCrimeWord(t2, returnOnlyLabels=True)
		pred = dd.isArticleSimilar(l+p+crime_type, t2)
		id1 = total[num1][0]
		id2 = total[num2][0]
		act = None
		if id1 in list1 and id2 in list1:
			act = 0
		else:
			act = 1
		
		#print(act, " ", int(pred))
		if pred:
			pred = 0
		else:
			pred = 1
		table[act][pred] += 1

	print(table, same, "line68")
