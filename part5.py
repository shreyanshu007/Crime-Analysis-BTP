# When the requested location is not present in the database

# Input - take new location
# Process - calculate its crime score and store into the DB
# Output - crime score of that location

from math import radians, cos, sin, asin, sqrt 
import math
import helper


# Takes Geo Cordinates of unknown locations(not in DB) and returns its crime score
def newLocationCrimeScoreFun(lat, lon):
	crime_score = 0

	for i in helper.locationExtractFromDB():
		sigma = 10					# Sigma if variance in KM
		radius = 3*sigma/100		# Radius is the acceptable range of angle in radian
		if helper.inRangeCheck(lat, lon, i[9], i[10], radius):
			# print(i[2])
			crime_factor = i[15] * (1 / (sigma * math.sqrt(2 * math.pi))) * math.exp((-1/2) * (helper.geoDistance(lat, lon, i[9], i[10]) / sigma) ** 2)
			crime_score += crime_factor
	return helper.normalizeCrimeScore(crime_score)





def main5(unknown_location):
	
	lat, lon = helper.getGeoCordinate(unknown_location)

	crime_score_of_unknown_location = newLocationCrimeScoreFun(lat, lon)

	# helper.addCrimeScoreAndLocationToDB(unknown_location, lat, lon, crime_score_of_unknown_location)

	return crime_score_of_unknown_location
