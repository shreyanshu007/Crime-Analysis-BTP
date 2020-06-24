# It takes the location form user and returns its crime score

# Input - Crime Locaiton
# Process - Get its GeoCordinates
# Process - If it is present in the DB retrive it
# Process - It not then calculate and store in the DB
# Output - Crime Score

import helper
import part5



def unknownLocationCrimeInfo(location):
	lat, lon = helper.getGeoCordinate(location)
	print(location, lat, lon)
	score = 0.0
	if helper.locationInDB(location, lat, lon):
		print("present")
		score = helper.getCrimeScore(location, lat, lon)
	else:
		print("absent")
		score = part5.main5(location)

	return score/helper.getMaxScore()
