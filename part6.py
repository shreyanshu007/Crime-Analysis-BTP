# This will identify if the article is duplicate or not

# Input - article
# Process - Find article in range of past and future 6 months
# Process - Will take two artilce and check if they have common crime type
# Process - And if they have common entities or not
# Output - False if duplicate, True if not duplicate


import helper
import pymysql
import sys
sys.path.append('/home/2016CSB1059/BTP')
from DuplicateDetection.duplicateDetection import DuplicateDetection

from nltk import word_tokenize

db_logfile  = '/home/2016CSB1059/BTP/logs/db_logfile.log'


def addDuplicateReference(articleId, dup_ref):
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "UPDATE NewsArticles SET DuplicateReferenceID = %s WHERE NewsArticleID = %s"
	try:
		db = connection.cursor()
		r = db.execute(sql, (dup_ref, articleId))
		#print(r)
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


def isDuplicate(article,st):

	# call duplicate check function
	d = DuplicateDetection(article[0], article[1] + " " + article[2], article[3], article[5], st, word_tokenize)
	d.crimeType()
	d.extractSelfEntities()
	ID = d.checkSimilarity()
	if not ID:
		addDuplicateReference(article[0], -1)
		return True
	else:
		'''
			TODO: Some how we need to merge the duplicate references
			to keep track of all duplicate articles.
		'''
		addDuplicateReference(article[0], ID)
		return False


# addDuplicateReference(1,1)
