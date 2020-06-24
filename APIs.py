#!/home/2016CSB1059/project_env/bin/python

'''import for python library'''
import requests
import json
import re
import ast
from datetime import datetime, timedelta
import pymysql
import sys
import time
'''adding path to import modules from appended location'''
import os
f = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f)
'''Following modules from above appended path.....'''
#import locationExtraction as le
#import main

'''
	Files names to add logs to 
'''
api_logfile = f + '/logs/api_logfile.log'
db_logfile  = f + '/logs/db_logfile.log'


'''
	Class to implement BING Spell Check API.
	Basic job is to make request for correct spelling
	These words are stored in DB table named: words
	if request is made in past DB is used to fetch to avoid 
	such request due to LIMITED REQUEST OFFERED BY API

	Some IMP vars(set this parameters):
	api		: API_KEY for the api
	endpoint	: URL to which request to made(available on api site)
	params,headers	: extra parameters for request.
'''
class SpellCheck(object):

	api 		= "2821db56077348ccbed8d8b8589fbea7"
	endpoint 	= "https://api.cognitive.microsoft.com/bing/v5.0/spellcheck"
	data 		= {}
	params 		= {
		"mkt"  : "en-us",
		"mode" : "proof" 
	}

	headers 	= {
		"Content-Type" : "application/x-www-form-urlencoded",
		"Ocp-Apim-Subscription-Key" : api
	}
	already_present_in_DB = []
	
	def set_data(self, text):
		'''
		Function to set reuested query
		input: text (queried text)
		'''
		self.data['text'] = text.lower()

	def is_form_inside_DB(self, forms):
		'''
			To check if queried request already present in DB.
			input: 
				forms:	string that is queried (i.e. wrong spelling)
					example: (mummbai is a form of mumbai)
			output: result - returning the row from DB.				
		'''
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		sql = "SELECT word_id, word, forms FROM words WHERE forms like %s"
		result = None
		try:
			db = connection.cursor()
			db.execute(sql, ("%"+forms+"%"))
			result = db.fetchall()
			connection.commit()
			db.close()
			connection.close()
		except Exception as e:
			#print(e)
			f = open(db_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while accessing DB table: word\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n")
			f.close()
			connection.rollback()
			connection.close()
		return result

	def filter_new_words(self):
		'''
			text/queried data is collection of words separated by some delimeter
			in order to reduce number of requests.
			This function separates out wrong spelling words that are never requested.
			IMP* : SET DATA BEFORE CALLING THIS FUNCTION
			output:
				new_text - words for request separated by comma
		'''
		words = self.data['text'].split(',')
		already_temps = []
		for word in words:
			result = self.is_form_inside_DB(word)
			if result:
				self.already_present_in_DB.append(result[0][1])
				already_temps.append(word)

		new_text = ""
		for word in words:
			if word not in already_temps:
				new_text += word + ","

		return new_text

	def spell_check(self):
		'''
			Main function to request API for spell check
			IMP* : SET DATA BEFORE CALLING THIS FUNCTION
			output:
				response.json()/None - json result of request result
		'''
		try:
			self.data['text'] = self.filter_new_words()
			#print(self.data['text'])
			if self.data['text'] == '' or not self.data['text']:
				return None
			response = requests.post(self.endpoint, headers=self.headers, params=self.params, data=self.data)
			# print(response)
			return response.json()
		except Exception as e:
			f = open(api_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while filtering list or requesting BING SPELL Check API\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()
			return None

	def is_word_inside_DB(self, word):
		'''
			input:
				word - to be queried
			output:
				result - row from DB
		'''
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		sql = "SELECT word_id, word, forms FROM words WHERE word like %s"
		result = None
		try:
			db = connection.cursor()
			db.execute(sql, ("%"+word+"%"))
			result = db.fetchall()
			connection.commit()
			db.close()
			connection.close()
		except Exception as e:
			# print(e)	
			f = open(db_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while accessing DB table: word\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()
			connection.rollback()
			connection.close()
		return result

	def add_word_form_to_DB(self, word, forms, new_word=True):
		'''
			TO add new words to DB after request.
		'''
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		if new_word:
			sql = "INSERT INTO words(forms, word) VALUES (%s, %s)"
		else:
			sql = "UPDATE words SET forms = %s WHERE word like %s"
		try:
			db = connection.cursor()
			if db.execute(sql, (forms, word)):
				rowId = connection.insert_id()

			connection.commit()
			db.close()
			connection.close()
		except Exception as e:
			# print(e)
			f = open(db_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while adding data to  DB table: word\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()

			connection.rollback()
			connection.close()		

	def convert_to_locations(self, json_response):
		'''
			The text was not single words.
			Therefore, this function joins all words in same order and returns to user.
			delimited by '|'
			input:
				json_repsonse: response of Spell Check api
			output:
				locations - string of locations separated by '|'
			IMP*: CALL AFTER YOU HAVE MADE THE REQUEST.
		'''
		location_text = self.data['text']
		if 'flaggedTokens' in  json_response:
			for item in json_response['flaggedTokens']:
				### adding corrected word to DB.
				correct_word = item['suggestions'][0]['suggestion']
				forms = item['token']
				result = self.is_word_inside_DB(correct_word)
				if result:
					forms = result[0][2] + "|" + forms
					self.add_word_form_to_DB(correct_word, forms, new_word=False)
				else:
					self.add_word_form_to_DB(correct_word, forms, new_word=True)
				### ===========================.
	
				tokens = location_text.split(item['token'])
				location_text = ''
				for tok in tokens[:-1]:
					location_text += tok + item['suggestions'][0]['suggestion']
				location_text += tokens[-1]
				# print(location_text)

		# print("Final set of locations: ", location_text)
		locations = location_text.split(',')[:-1]
		locations += self.already_present_in_DB
		#print(locations)
		return locations


'''
	Class to implement LocationIQ API
	This API returns geo-cordinates and 
	other related information about requested location.
	These data are stored in LocationInfo table of DB.
	
	Some Imp vars:
	api	: API KEY
	url	: ENDPOINT where request to be made
	count 	: to count number of requests as requests were limited.
'''
class LocationIQ(object):

	api 		= 'pk.270ff7f1f6671b75509ce3f0a0abc130'
	url 		= "https://api.locationiq.com/v1/autocomplete.php"
	count 		= 0

	def return_location_details(self, loc, knownRequest=True):
		'''
			To return details of the requested location
			loc.
			input:
				loc: location Name
				knownRequest: to check if request already present in DB. 
			output:
				db_location_details - details of location from request.
		'''
		data = {
			'key' : self.api,
			'q'   : loc
		}

		try:
			if self.count <= 1000:
				response = requests.get(self.url, params = data)
				self.count += 1
			else:
				## sleep for X seconds
				## until api refreshes
				current = datetime.now()
				next_day = datetime.now() + timedelta(days=1)
				next_day.replace(hour=1, minute=0, second=0)
				sleep_time = abs((next_day - current).total_seconds())
				time.sleep(sleep_time)
				#print("Sleeping for N seconds")
				#time.sleep(5)
				response = requests.get(self.url, params = data)
				self.count = 1
		except Exception as e:
			#print(e)
			# Log_file.write("Following error occurred while requesting LocationIQ: \n" + str(sys.exc_info()) + "\n\n")
			f = open(api_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while LocationIQ request/date calculation DB table: word\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()

			return {}

		
		details = ast.literal_eval(response.text)[0]
		db_location_details = {}

		if details:

			if details['type'] in ['city', 'state', 'country'] or knownRequest:
				return None

			db_location_details['queried_name'] 	= loc
			db_location_details['display_name'] 	= details['display_place']
			db_location_details['class_type']		= details['class']
			db_location_details['location_type']	= details['type']
			db_location_details['osm_type']			= details['osm_type']
			db_location_details['lat']	 			= details['lat']
			db_location_details['lon']	 			= details['lon']
			db_location_details['min_lat']	 		= details['boundingbox'][0]
			db_location_details['max_lat']	 		= details['boundingbox'][1]
			db_location_details['min_lon']	 		= details['boundingbox'][2]
			db_location_details['max_lon']	 		= details['boundingbox'][3]

			try:
				db_location_details['postcode']		= details['address']['postcode']
				db_location_details['city']             = details['address']['city']
				db_location_details['state']            = details['address']['state']
			except Exception as e:

				f = open(api_logfile, 'a')
				f.write("======== Log written on " + str(datetime.now())+ "========\n")
				f.write("Error while data extraction form API request.\n")
				f.write(str(e))
				f.write("======================== End of error ====================\n\n" )
				f.close()
		
		return db_location_details


	def insert_into_database(self, data, crime_score):
		'''
			To insert api response into DB
			input:
				data - api response from fruncton return_location_details()
			output:
				crime_score - calculated by framework.
		'''
		modified_data = (data['queried_name'].lower(), data['display_name'].lower(), data['city'].lower(), data['state'].lower(), data['postcode'], data['class_type'].lower(), data['location_type'].lower(), data['osm_type'].lower(), float(data['lat']), float(data['lon']), float(data['min_lat']), float(data['max_lat']), float(data['min_lon']), float(data['max_lon']), crime_score)
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		sql = "INSERT INTO LocationInfo(queried_name, display_name, city, state, postcode, class, type, osm_type, lat, lon, min_lat, max_lat, min_lon, max_lon, crime_score) \
	     values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		try:
			db = connection.cursor()
			if db.execute(sql, modified_data):
				rowId = connection.insert_id()

			connection.commit()
			db.close()
			connection.close()
		except Exception as e:
			#print(e)
			f = open(db_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while adding data to DB table: LocationInfo\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()
			connection.rollback()
			connection.close()


	def is_location_exists_in_db(self, location):

		location = location.lower()
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		sql = "SELECT lat, lon FROM LocationInfo WHERE queried_name LIKE %s OR display_name LIKE %s"
		try:
			db = connection.cursor()
			db.execute(sql, ("%"+location+"%", "%"+location+"%"))
			result = db.fetchall()
			connection.commit()
				
		except Exception as e:
			#print(e)
			f = open(db_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while accessing DB table: LocationInfo\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()
			connection.rollback()

		finally:
			db.close()
			connection.close()
			if result:
				return result[0]
			else:
				return False

	def update_location(self, location, crime_score):

		modified_data = (crime_score, "%" + location.lower() + "%")
		connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
		sql = "UPDATE LocationInfo SET crime_score = crime_score + %s WHERE queried_name LIKE %s"
		try:
			db = connection.cursor()
			if db.execute(sql, modified_data):
				rowId = connection.insert_id()

			connection.commit()
			db.close()
			connection.close()
		except Exception as e:
			# print(e)
			f = open(db_logfile, 'a')
			f.write("======== Log written on " + str(datetime.now())+ "========\n")
			f.write("Error while accessing DB table: LocationInfo\n")
			f.write(str(e))
			f.write("======================== End of error ====================\n\n" )
			f.close()
			connection.rollback()
			connection.close()


	

if __name__ == '__main__':

	'''articles = le.transfer()
	count = 1
	for article in articles[11:]:
		print("article: ", count)
		count += 1
		if main.fileCrimeClassify.classifyCrime(article) == 'crime' and article[3]:
			score = main.crimeScore(main.fileCrimeClassify.extractCrimeWord(article)[0], article[3])
			locations =  le.extractCrimeLocations(article[1] + ' ' + article[2])

			locs = ''
			for loc in locations:
				locs += loc + ', '
			
			spell_checker = SpellCheck()
			spell_checker.set_data(locs)
			response = spell_checker.spell_check()
			locations = spell_checker.convert_to_locations(response)
			
			print(locations)
			
			LIQ = LocationIQ()
			for loc in locations:
				if LIQ.is_location_exists_in_db(loc):
					LIQ.update_location(loc, score)
					continue

				location_details_dict = LIQ.return_location_details(loc)
				LIQ.insert_into_database(location_details_dict, score)



	locations = le.extractCrimeLocations(text)'''
	sc = SpellCheck()
	sc.set_data('helllo')
	print(sc.spell_check())
	print(sc.is_form_inside_DB('helllo'))
	print(sc.is_word_inside_DB('hello'))
	print(sc.add_word_form_to_DB('mumbai','mummbai', new_word=True))
	print(sc.add_word_form_to_DB('mumbai','mummbai|Muumbai', new_word=False))
	'''liq = LocationIQ()
	for i in range(6):
		liq.return_location_details("delhi")
	pass'''

	
