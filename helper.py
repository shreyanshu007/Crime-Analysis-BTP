#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python


# new crime score calculation method


from math import radians, cos, sin, asin, sqrt 

import pymysql
import sys
import math
from datetime import datetime
from APIs import LocationIQ

db_logfile  = '/home/2016CSB1059/BTP/logs/db_logfile.log'


# Takes the Raw Crime Score and returns the normalized Crime Score, also update the Max Crime Score if required.
def normalizeCrimeScore(crime_score):
	max_score = getMaxScore()
	if crime_score > max_score:
		max_score = crime_score
		updateMaxScore(max_score)
	return crime_score/max_score


# Takes the number of days and return the decay factor for crime score with half life being 180 days
def decayFactor(x_days):
	return math.exp(-math.log(2,math.e) * x_days / 180.0)

# Takes the location and its lat, lon and returns the latest date when the crime score for that location was updated
def getLastUpdateDate(location, lat, lon):
	location = location.lower()
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT LastModifiedDate FROM LocationInfo WHERE (queried_name LIKE %s OR display_name LIKE %s) AND lat = %s AND lon = %s"
	try:
		db = connection.cursor()
		db.execute(sql, ("%"+location+"%", "%"+location+"%", lat, lon))
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
			return result[0][0]
		else:
			return None

# Returns the Max Crime Score
def getMaxScore():
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT MAX(crime_score) FROM LocationInfo"
	try:
		db = connection.cursor()
		db.execute(sql, )
		result = db.fetchall()
		connection.commit()
			
	except Exception as e:
		print(e)
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
			return result[0][0]
		else:
			return None

# Updates the Max Crime Score
def updateMaxScore(max_score):
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "UPDATE MaxScore SET max_score = %s"
	try:
		db = connection.cursor()
		db.execute(sql, (max_score))
		connection.commit()
	except Exception as e:
		#print(e)
		f = open(db_logfile, 'a')
		f.write("======== Log written on " + str(datetime.now())+ "========\n")
		f.write("Error while accessing DB table: MaxScore\n")
		f.write(str(e))
		f.write("======================== End of error ====================\n\n" )
		f.close()
		connection.rollback()
	finally:
		db.close()
		connection.close()

# Takes the location and its lat, lon and returns its crime score 
def getCrimeScore(location_name, lat, lon):
	location = location_name.lower()
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT crime_score FROM LocationInfo WHERE (queried_name LIKE %s OR display_name LIKE %s) AND lat = %s AND lon = %s"
	try:
		db = connection.cursor()
		db.execute(sql, ("%"+location+"%", "%"+location+"%", lat, lon))
		result = db.fetchall()
		connection.commit()
			
	except Exception as e:
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
			file = open('check.txt','w')
			file.write(str(result))
			return result[0][0]
		else:
			return None

# Adds the new crime location with its crime score to DB
def addCrimeScoreAndLocationToDB(crime_score, data):
	modified_data = (data['queried_name'].lower(), data['display_name'].lower(), data['city'].lower(), data['state'].lower(), data['postcode'], data['class_type'].lower(), data['location_type'].lower(), data['osm_type'].lower(), float(data['lat']), float(data['lon']), float(data['min_lat']), float(data['max_lat']), float(data['min_lon']), float(data['max_lon']), crime_score, datetime.now())
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "INSERT INTO LocationInfo(queried_name, display_name, city, state, postcode, class, type, osm_type, lat, lon, min_lat, max_lat, min_lon, max_lon, crime_score, LastModifiedDate) \
     values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
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
		f.write("Error while accessing DB table: LocationInfo\n")
		f.write(str(e))
		f.write("======================== End of error ====================\n\n" )
		f.close()
		
		connection.rollback()
		connection.close()

# Takes the location and its lat, lon and update its crime_score 
# And also updates the last update date of that location
def updateCrimeScore(location_name, lat, lon, updated_score):
	modified_data = (updated_score, datetime.now(), "%" + location_name.lower() + "%", "%" + location_name.lower() + "%", lat, lon)
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "UPDATE LocationInfo SET crime_score = %s, LastModifiedDate = %s  WHERE (queried_name LIKE %s OR display_name LIKE %s) AND lat = %s AND lon = %s"
	try:
		db = connection.cursor()
		if db.execute(sql, modified_data):
			rowId = connection.insert_id()

		connection.commit()
		db.close()
		connection.close()
	except Exception as e:
		print(e)
		f = open(db_logfile, 'a')
		f.write("======== Log written on " + str(datetime.now())+ "========\n")
		f.write("Error while accessing DB table: LocationInfo\n")
		f.write(str(e))
		f.write("======================== End of error ====================\n\n" )
		f.close()
		connection.rollback()
		connection.close()

# Takes the location name and returns its geoCordinates
def getGeoCordinate(location_name):
	location = location_name.lower()
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT lat, lon FROM LocationInfo WHERE queried_name LIKE %s OR display_name LIKE %s"
	try:
		db = connection.cursor()
		db.execute(sql, ("%"+location+"%", "%"+location+"%"))
		result = db.fetchall()
		connection.commit()
			
	except Exception as e:
		print(e)
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
			LIQ = LocationIQ()
			details = LIQ.return_location_details(location, False)
			return float(details['lat']), float(details['lon'])

# Takes the location, its lat and lon and returns True if it is present in DB otherwise it returns False
def locationInDB(location, lat, lon):
	location = location.lower()
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT lat, lon FROM LocationInfo WHERE (queried_name LIKE %s OR display_name LIKE %s) AND lat = %s AND lon = %s"
	result = None
	try:
		db = connection.cursor()
		db.execute(sql, ("%"+location+"%", "%"+location+"%", lat, lon))
		result = db.fetchall()
		connection.commit()
			
	except Exception as e:
		print(e)
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
			return True
		else:
			return False

# Extracts all the location and its info from LocationInfo table
def locationExtractFromDB():

	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT * FROM LocationInfo"
	try:
		db = connection.cursor()
		db.execute(sql,)
		result = db.fetchall()
		connection.commit()
		db.close()
		connection.close()
		if result:
			return result
		else:
			return False
			
	except Exception as e:
		print(e)
		f = open(db_logfile, 'a')
		f.write("======== Log written on " + str(datetime.now())+ "========\n")
		f.write("Error while accessing DB table: LocationInfo\n")
		f.write(str(e))
		f.write("======================== End of error ====================\n\n" )
		f.close()
		connection.rollback()
		connection.close()


# Takes two Geo Cordiantes in degree and returns True if they are in range otherwise returns False
def inRangeCheck(lat1, lon1, lat2, lon2, radius):
	acceptable_lat = radius
	acceptable_lon = radius
	if abs(lat2- lat1) < acceptable_lat and abs(lon2 - lon1) < acceptable_lon:
		# print('yes')
		return True
	else:
		# print('no')
		return False


# Takes two Geo Cordinates and returns the distance between them
def geoDistance(lat1, lon1, lat2, lon2): 
	
	# The math module contains a function named 
	# radians which converts from degrees to radians. 
	lon1 = radians(lon1) 
	lon2 = radians(lon2) 
	lat1 = radians(lat1) 
	lat2 = radians(lat2) 
	
	# Haversine formula 
	dlon = lon2 - lon1 
	dlat = lat2 - lat1 
	a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2

	c = 2 * asin(sqrt(a)) 
	
	# Radius of earth in kilometers. Use 3956 for miles 
	r = 6371
	
	# calculate the result 
	return(c * r) 
	
	



# driver code 
# lat1 = 18.5326525
# lat2 = 53.31861111111111
# lon1 = 73.9470036
# lon2 = -1.6997222222222223

# print(newCrimeScoreFun(lat1, lon1))

# for i in locationExtractFromDB():
# 	print(i[2])
# 	print(i[9])
# 	print(i[10])
# 	print(i[15])
# 	break


'''
0 location_id  
1 queried_name                    
2 display_name                             
3 city          
4 state              
5 postcode  
6 class     
7 type              
8 osm_type  
9 lat          
10 lon               
11 min_lat      
12 max_lat      
13 min_lon       
14 max_lon       
15 crime_score        
'''

# print(geoDistance(lat1, lat2, lon1, lon2), "K.M") 
