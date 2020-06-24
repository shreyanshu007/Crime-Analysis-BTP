#!/home/2016CSB1059/project_env/bin/python

# Takes all the unprocessed articles stored in the past in DB and extract its details store in DB
# main trigger function  --------------- comment by shailendra

# Input - Stored Article
# Process - If it is a Crime Article then Location is extracted from that artilce
# Process - Article is added to the Article DB with all the extracted details
# Process - Crime Score of that locaiton is calculated and updated in the Location DB
# Output - 



from datetime import datetime
import pymysql
import math
import csv
import sys

import helper
import part4
import part6

import os
f = os.path.dirname(os.path.abspath(__file__))
article_logfile = f + '/logs/article_logfile.log'
db_logfile      = f + '/logs/db_logfile.log'

# Fetches all the articles from the DB
def fetchAllArticles(startID, endID):
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT * FROM NewsArticles WHERE NewsArticleID BETWEEN %s AND %s AND AnalyzedBy IS NULL AND DuplicateReferenceId IS NULL"
	result = None
	try:
		db = connection.cursor()
		db.execute(sql,(startID, endID))
		result = db.fetchall()
		connection.commit()
		
	except Exception as e:
		# print("exception ", e)
		f = open(db_logfile, 'a')
		f.write("======== Log written on " + str(datetime.now())+ "========\n")
		f.write("Error while accessing DB table: NewsArticles\n")
		f.write(str(e))
		f.write("======================== End of error ====================\n\n" )
		f.close()

		connection.rollback()
	finally:
		# print("finally")
		db.close()
		connection.close()

	return result


def startSystemTrigger():
	#articles = fetchAllArticles()
	start = 350000
	end   = 400000
	batch = 1
	while True:
		articles = fetchAllArticles(start, end)
		print(len(articles))
		if not articles:
			break
		print("ashdjdgs")
		frs = open(f + '/logs/framework_running_status.log','a')
		frs.write("===========================Starting batch: " + str(batch) + "===============================\n")
		frs.close()
		for i,article in enumerate(articles):
			# print("articleID: ", article[0])
			# for each article....
			# if : # if given article is duplicate or not...
			# 	# if not duplicate proceed with further processing
			# 	print("article ", article[0], " is not duplicate and is sent for processing")
			if i%5000 == 0:
				frs = open(f + '/logs/framework_running_status.log','a')
				frs.write("No. of articles processed: " + str(start + i) + "\n")
				frs.close()
			#try:
			part4.processArticle(article)
			'''except Exception as e:
				print(e)
				f = open(article_logfile, 'a')
				f.write("======== Log written on " + str(datetime.now())+ "========\n")
				f.write("Error while processing article: " + str(article[0]) + "iteration no.:" + str(i) + "\n")
				f.write(str(e))
				f.write("\n======================== End of error ====================\n\n" )
				f.close()'''
				### TODO: proper log file writing part.
				# Log_file.write("Following error occurred while processing article ID: " + str(article[0]) + " \n" + str(e) + "\n" + str(sys.exc_info()) + "\n\n")

		start += 50000
		end   += 50000
		batch += 1
		frs = open(f + '/logs/framework_running_status.log','a')
		frs.write("===========================================================================\n")
		frs.close()
			# else:
			# 	print("article is duplicate")





if __name__ == '__main__':
	#try:
	startSystemTrigger()
	'''except Exception as e:
		print("System failed to start due to following error")
		print(e)'''
