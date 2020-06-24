# This should be triggired after every fixed interval

# Input - 
# Process - When triggired after x days
# Process - run through complete location DB
# Process - decay crime score every location
# Output - 


import helper


def main3(x_days):

	for i in helper.locationExtractFromDB():
		updated_score = i[15] * helper.decayFactor(x_days)
		helper.updateCrimeScore(location_name, lat, lon, updated_score)


