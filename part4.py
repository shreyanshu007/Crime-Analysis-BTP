# After the Article is crawled it is added to the DB with all the details
# processing of items ----------- shailendra

# Input - Crawled Article
# Process - If it is a Crime Article then Location is extracted from that artilce
# Process - Article is added to the Article DB with all the extracted details
# Process - Crime Score of that location is calculated and updated in the Location DB
# Output - 

# Required text file "CrimeScoreDict.csv"


import LocationExtraction.locationExtraction as fileLocationExtract
import CrimeClassification.MainCrimeClassifier as fileCrimeClassify
from datetime import datetime
import pymysql
import math
import csv
import sys
import os
import helper
import part6

f = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f)
from APIs import SpellCheck, LocationIQ
from nltk.tag import StanfordNERTagger
st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') # doctest: +SKIP

db_logfile  = f + '/logs/db_logfile.log'

# Reads the weights of different crimes and stores the value in mydict dictionary
with open(f + '/CrimeClassification/CrimeScoreDict.csv') as csv_file:
	reader = csv.reader(csv_file)
	mydict = dict(reader)


# Returns the gap of days between two dates taken as input.
def dayGap(date1, date2):
	# print(date1," : ", date2)
	date1 = str(date1).split(' ')[0].split('-')
	date2 = str(date2).split(' ')[0].split('-')
	# print(date1," : ", date2)
	return abs(365*(int(date1[0]) - int(date2[0])) + 30*(int(date1[1]) - int(date2[1])) + (int(date1[2]) - int(date2[2])))


# Returns the crime socre of an article after the decay on the basis of number of days past by.
def crimeScore(crime, time):
	return float(mydict[crime])*helper.decayFactor(dayGap(time, datetime.now()))

def add_entities_info_to_DB(articleId, entities_dict):
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "UPDATE NewsArticles SET entities_dict = %s WHERE NewsArticleID = %s"
	try:
		db = connection.cursor()
		entities_dict = str(entities_dict)
		# entities_dict = entities_dict.replace("'", "")
		# entities_dict = entities_dict.replace('"', "")
		db.execute(sql, (entities_dict, articleId))
		connection.commit()
	except Exception as e:
		#print(e)
		f = open(db_logfile, 'a')
		f.write("======== Log written on " + str(datetime.now())+ "========\n")
		f.write("Error while accessing DB table: NewsArticles\n")
		f.write(str(e))
		f.write("======================== End of error ====================\n\n" )
		f.close()
		connection.rollback()
	finally:
		db.close()
		connection.close()


def processArticle(article):

	# print(fileCrimeClassify.classifyCrime(article), fileCrimeClassify.classifyCrime(article) == 'crime', article[3], part6.isDuplicate(article, st))
	if fileCrimeClassify.classifyCrime(article) == 'crime' and article[3] and part6.isDuplicate(article, st):
		#print("came")

		text = article[1] + ' ' + article[2]
		crime_score = crimeScore(fileCrimeClassify.extractCrimeWord(text)[0], article[3])
		location_list, entities_dict =  fileLocationExtract.extract_potential_locations(text)
		'''Adding entities Info to DB'''
		add_entities_info_to_DB(article[0], entities_dict)
		# TODO: Decide which and how many location you want to choose
		# Remove city and state from the location_list
		# Location we get from LocationIQ should belong to the same city our article belogs to.
		article_city = article[5]
		filtered_location_list = []
		# locs = ''
		# for loc in location_list:
		# 	locs += loc + ', '
		
		spell_checker = SpellCheck()
		location_text = ",".join(location_list)
		
		spell_checker.set_data(location_text)
		response = spell_checker.spell_check()
		if response:
			locations = spell_checker.convert_to_locations(response)
		else:
			locations = location_list
		# print(locations)
		# print("\nExtracted set of locations from article ", article[0]," as follows also crime score is -> ", crime_score, " :")
		#print(locations)
		
		LIQ = LocationIQ()
		for location in locations:
			lat, lon = helper.getGeoCordinate(location)
			if helper.locationInDB(location, lat, lon):
				# LIQ.update_location(loc, score)
				updated_score = helper.getCrimeScore(location, lat, lon) * helper.decayFactor(dayGap(helper.getLastUpdateDate(location, lat, lon), datetime.now())) + crime_score
				# helper.updateCrimeScore(location, lat, lon, updated_score)
				helper.updateCrimeScore(location, lat, lon, updated_score)
				# print("update successful")
				continue
			#print(location)
			location_details_dict = LIQ.return_location_details(location)
			#print(location_details_dict)
			if location_details_dict:
				helper.addCrimeScoreAndLocationToDB(crime_score, location_details_dict)
				# print("insert successful")
	else:
		if fileCrimeClassify.classifyCrime(article) != 'crime':
			part6.addDuplicateReference(article[0], -2)
			#print("Article is non-crime article")
		elif not article[3]:
			part6.addDuplicateReference(article[0], -3)
			#print("Date is empty")
		#else:
		#	print("Article is duplicate") 		
		# print("Article is either duplicate or non-crime or has date empty")
		# for location in location_list:

			# Use LocationIQ API to get detailed list of similar locations

			# For loc in list_of_location_returned_from_API

				# If loc is a city or a state -> Remove it from the list

				# If city of the loc in not same as article_city -> Remove it from the list

				# Else add that loc to filtered_location_list


		# for location in filtered_location_list:

		# 	addArticleToDB(article, location)

		# 	lat, lon = helper.getGeoCordinate(location)
		# 	if helper.locationInDB(location, lat, lon):
				
		# 	else:
		# 		helper.addCrimeScoreAndLocationToDB(location, lat, lon, crime_score)


