#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python


# Extract location info and create a geojson file required of heatmap


import helper



extData = helper.locationExtractFromDB()
# print(extData[0][9])
# print(extData[0][10])
# print(extData[0][15])



# id = 0
# lat = 9
# lon = 10
# crime_socre = 15 


file1 = open('location_and_crimeScore.geojson', 'w') 

start = '{"type": "FeatureCollection","crs": { "type": "name", "properties": { "name": "urn:ogc:def:crs:OGC:1.3:CRS84" } },"features": ['

middle1 = '{ "type": "Feature", "properties": { "id": "'

middle2 = '", "mag": '

middle3 = ', "time": 1507425650893, "felt": null, "tsunami": 0 }, "geometry": { "type": "Point", "coordinates": [ '

middle4 = ' ] } }'

# middle = '{ "type": "Feature", "properties": { "id": "ak16994521", "mag": 2.3, "time": 1507425650893, "felt": null, "tsunami": 0 }, "geometry": { "type": "Point", "coordinates": [ -151.5129, 63.1016, 0.0 ] } }'

comma = ','

end = ']}'


file1.write(start)

ind = 0

for loc in extData:
	if ind > 0:
		file1.write(comma)

	ind += 1

	file1.write(middle1)
	file1.write(str(ind))
	file1.write(middle2)
	file1.write(str(loc[15]))
	file1.write(middle3)
	file1.write(str(loc[10]))
	file1.write(comma)
	file1.write(str(loc[9]))
	file1.write(middle4)






# crime_score_datav1.csv



import csv

with open('crime_score_datav1.csv') as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')
	ind += 1
	for row in csv_reader:
		if row[2] != 0:
			if ind > 0:
				file1.write(comma)
			file1.write(middle1)
			file1.write(str(ind))
			file1.write(middle2)
			file1.write(str(row[0]))
			file1.write(middle3)
			file1.write(str(row[1]))
			file1.write(comma)
			file1.write(str(row[2]))
			file1.write(middle4)



file1.write(end)



file1.close()



# import sys
# import requests
# import json
# import urllib.request
# from bs4 import BeautifulSoup
# from selenium import webdriver
# import pandas as pd
# import re
# import ast
# from datetime import datetime

# Log_file = open('logfile.log', 'w')
# Log_file.write("================================================================================================================================\n" + str(datetime.now()) + "\n================================================================================================================================\n\n")

# sys.path.append('/home/2016CSB1059/BTP/LocationExtraction/')

# import locationExtraction as le

# text = '''Man, 26, dies of electrocution in Mumbai

# Updated: Sep 08, 2019 01:55 IST

# A 26-year-old worker died after he sustained an electric shock during the renovation work of a room in Vikhrol Kanamawar Nagar on Thursday afternoon. Police probe revealed that adequate precautions were not taken to ensure safety of the workers and therefore booked the contractor.

# According to the police, the victim, Jagganath Anantgiri, is a resident of Kanamawar Nagar. Police said that during the renovation work, the wiring board in the room was kept hanging haphazardly from the roof of the house.p
# s
# "Anantgiri sustained a shock after coming in contact with a livewire and collapsed. He succumbed while being rushed to the hospital," said an officer from Vikhroli police station. The police are in process to identify the other accused responsible for the incident. The accused have been booked under Section 304A (causing death by negligence) of the Indian Penal Code (IPC).

# First Published: Sep 08, 2019 00:34 IST'''

# '''function call to extract locations from text'''





# class SpellCheck(object):

# 	api 		= "3b35cb9302ac45459c680337f185958e"
# 	endpoint 	= "https://api.cognitive.microsoft.com/bing/v7.0/spellcheck"
	
# 	def spellCheck(self, text):
		



# locations = le.extractCrimeLocations(text)

# print(locations)

# locs = ''
# for loc in locations:
# 	locs += loc + ', '

# example_text = locs

# api_key = "3b35cb9302ac45459c680337f185958e"

# endpoint = "https://api.cognitive.microsoft.com/bing/v7.0/spellcheck"

# data = {"text" : example_text}

# params = {
# 	"mkt" : "en-us",
# 	"mode": "proof"
# 	}

# headers = {
# 	"Content-Type" : "application/x-www-form-urlencoded",
# 	"Ocp-Apim-Subscription-Key" : api_key
# 	}

# response = requests.post(endpoint, headers=headers, params=params, data=data)

# print(response)
# json_response = response.json()

# # print(json_response)
# for item in json_response['flaggedTokens']:
# 	tokens = example_text.split(item['token'])
# 	example_text = ''
# 	for tok in tokens[:-1]:
# 		example_text += tok + item['suggestions'][0]['suggestion']
# 	example_text += tokens[-1]
# 	print(example_text)

# print("Final set of locations: ", example_text)


# locations = example_text.split(',')[:-1]
# print(locations)

# url = "https://api.locationiq.com/v1/autocomplete.php"

# for loc in locations:
# 	data = {
# 		'key' : 'pk.270ff7f1f6671b75509ce3f0a0abc130',
# 		'q'   : loc
# 	}
	
# 	response = requests.get(url, params = data)

# 	## print(response.text[0])
# 	details = ast.literal_eval(response.text)
# 	details = details[0]
	
# 	''' Separating out required information fromm requested api details '''
# 	db_location_details = {}
# 	db_location_details['queried_name'] 	= loc
# 	db_location_details['display_name'] 	= details['display_place']
# 	db_location_details['city'] 			= ''
# 	db_location_details['state'] 			= details['address']['state']
# 	try:
# 		db_location_details['postcode']			= details['address']['postcode']
# 	except:
# 		print("For queried location: ", loc,", following Error occurred: \n", sys.exc_info())
# 		Log_file.write("For queried location: " + str(loc) + ", following Error occurred: \n" + str(sys.exc_info()) + "\n\n")
# 	db_location_details['class_type']		= details['class']
# 	db_location_details['location_type']	= details['type']
# 	db_location_details['osm_type']			= details['osm_type']
# 	db_location_details['lat']	 			= details['lat']
# 	db_location_details['lon']	 			= details['lon']
# 	db_location_details['min_lat']	 		= details['boundingbox'][0]
# 	db_location_details['max_lat']	 		= details['boundingbox'][1]
# 	db_location_details['min_lon']	 		= details['boundingbox'][2]
# 	db_location_details['max_lon']	 		= details['boundingbox'][3]
	
# 	print("Details extracted for given location:\n")
# 	for item in db_location_details:
# 		print(item, "\t", db_location_details[item])
	

