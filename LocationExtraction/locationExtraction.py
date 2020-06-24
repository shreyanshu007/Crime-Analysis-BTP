#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python

# modules to import
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from pprint import pprint
import pymysql
from nltk.tag import StanfordNERTagger
import nltk
from nltk import word_tokenize, pos_tag, ne_chunk, sent_tokenize
from nltk import RegexpParser
from nltk import Tree
import pandas as pd

from nltk.corpus import wordnet
import operator
from collections import Counter 
import re
import os

# stanford tagger initialization
st = StanfordNERTagger('english.all.3class.distsim.crf.ser.gz') # doctest: +SKIP

# nlp tagger initialization
nlp = en_core_web_sm.load()

# NE_LIST
NE_LIST = ['PERSON', 'LOCATION' ,'GPE', 'ORGANIZATION']

COMMON_WORDS_IN_LOCATION = ['village', 'colony', 'bhawan', 'bhavan','pradesh','ashram','nagar','vihar','chowk','road','area','sector','garden','park','camp','crossing','garh','ganj', 'mandi', 'beach', 'house', 'ghat']

PORTER = nltk.PorterStemmer()

COMMON_PRECEEDING_LIST = ['in', 'from', 'at', 'near', 'around', 'central', 'east', 'west', 'north', 'south']
# SUCCEEDING_LIST = ['police', 'cop']


f = os.path.dirname(os.path.abspath(__file__))
ind = f.rfind('/')
def returnCrimeWordScores(filename=f[:ind] + "/CrimeClassification/CrimePhrases.txt"):
	'''
		To extract all crime words stored in given text file.
		input: filename - name of file containing crime words each line
		output: crime word dict with respective score 
	'''
	CrimePhrasesDict = {}
	with open(filename, "r+") as file:
		for word in file.read().split('\n'):
			processed_word = PORTER.stem(word.lower())
			for syn in wordnet.synsets(word):
				if processed_word == PORTER.stem(syn.lemmas()[0].name()):
					if processed_word in CrimePhrasesDict.keys():
						CrimePhrasesDict[processed_word] += len(syn.definition().split(';'))
					else:
						CrimePhrasesDict[processed_word] = 1 + len(syn.definition().split(';'))

	return CrimePhrasesDict


crimeWordScore = returnCrimeWordScores()
CRIME_WORD_STEM_LIST = [word for word in crimeWordScore.keys()]


def get_continuous_chunks_from_tagged_sentences(tagged_sent):
	### given dict of tagged sentences returns continuous chunks of Tagged Entities
	### Exmaple: {'Shailendra' : 'PERSON', 'Gupta' : 'PERSON', 'and' : 'O'}
	### Returned list will be: ['Shailendra Gupta']
	continuous_chunk = []
	current_chunk = []

	for token, tag in tagged_sent:
		if tag != "O":
			current_chunk.append((token, tag))
		else:
			if current_chunk: # if the current chunk is not empty
				continuous_chunk.append(current_chunk)
				current_chunk = []
	# Flush the final current_chunk into the continuous_chunk, if any.
	if current_chunk:
		continuous_chunk.append(current_chunk)
	return continuous_chunk


# returns dict of tagged entities
def stanfordTagger(text):
	### Using Stanford Tagger the function returns dict of tagged entities
	'''
		To tag a given text using stanford tagger
		input: text
		output: entities - dictionary of entities and their respective tags
			example: {'Chandigarh':'LOCATION', 'IIT':'ORGANIZATION',
					'Rahul': 'PERSON'}
	'''
	chunkLabels = []
	chunkList = word_tokenize(text)
	results = st.tag(chunkList)
	# print(results)
	entities = {}
	prev = [results[0]]
	total = None
	for tags in results[1:]:
		if tags[1] == prev[0][1]:
			prev.append(tags)
		else:
			total = prev
			prev = [tags]
			if total[0][1] != 'O':
				entity = total[0][0]
				for item in total[1:]:
					entity += ' ' + item[0]

				if entity not in entities.keys() or entities[entity] != 'LOCATION':
					entities[entity] = total[0][1]
	
	return entities

# run select sql query and fetch required data
def fetch_query_output(query, data=None):
	'''
		To fetch query output.
		input: query - query to issue to DB.
			data - data to add in SQL query.
		output: result of query
	'''
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = query
	text = None
	try:
		with connection:
			db = connection.cursor()
			db.execute(sql,(data))
			text = db.fetchall()
			connection.commit()
	except Exception as e:
		connection.rollback()
	finally:
		db.close()
		connection.close()
	return text


def get_continuous_chunks(text, chunk_func=ne_chunk):
	chunked = chunk_func(pos_tag(word_tokenize(text)))
	continuous_chunk = []
	current_chunk = []

	for subtree in chunked:
		if type(subtree) == Tree:
			current_chunk.append(" ".join([token for token, pos in subtree.leaves()]))
		elif current_chunk:
			named_entity = " ".join(current_chunk)
			if named_entity not in continuous_chunk:
				continuous_chunk.append(named_entity)
				current_chunk = []
		else:
			continue

	# print(continuous_chunk)
	return continuous_chunk

# returns entities tagged by NLTK
def nltkTagger(Text):
	### Using NTTK Tagger the function returns dict of tagged entities
	'''
		To tag a given text using NLTK tagger
		input: text
		output: entities - dictionary of entities and their respective tags
			example: {'Chandigarh':'LOCATION', 'IIT':'ORGANIZATION',
					'Rahul': 'PERSON'}
	'''

	Locations = []
	prepLocations = []
	Entities = {}
	crime_word_list = []
	names = []

	sentences = nltk.sent_tokenize(Text)

	for sent in sentences:
		words = nltk.word_tokenize(sent.lower())
		for word in words:
			if PORTER.stem(word) in CRIME_WORD_STEM_LIST:
				crime_word_list.append(word)

		chunks = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)))
		length = len(chunks)
		for i in range(length):
			curr = chunks[i]
			if i == 0 and length != 1:
				prev = None
				Next = chunks[i+1]

			elif i == length-1:
				prev = chunks[i-1]
				Next = None

			else:
				prev = chunks[i-1]
				Next = chunks[i+1]

			if curr and hasattr(curr, 'label'):
				if prev and Next and hasattr(prev, 'label') and hasattr(Next, 'label'):
					item = ' '.join(c[0] for c in prev) + ' ' + ' '.join(c[0] for c in curr) + ' ' + ' '.join(c[0] for c in Next)
					Entities[item] = curr.label()
				elif prev and hasattr(prev, 'label'):
					Entities[item] = curr.label()
				elif Next and hasattr(Next, 'label'):
					item = ' '.join(c[0] for c in curr) + ' ' + ' '.join(c[0] for c in Next)
					Entities[item] = curr.label()
				else:
					item = ' '.join(c[0] for c in curr)
					Entities[item] = curr.label()

	return Entities

# common tagged entities from both tagger
# assuming Stanford to be strong prediction over NLTK
def bothTagger(text):
	'''
		input: text 
		output: dictionary of entities
			More preference to Stanford Tagger
	'''
	ent1 = nltkTagger(text)
	ent2 = stanfordTagger(text)

	entities = {}

	for e in ent1:
		if e in ent2:
			entities[e] = ent2[e]

	return entities

def isPotentialLocation(location, text):
	'''
		To check if any entity can be potential location or not.
	'''
	for item in COMMON_WORDS_IN_LOCATION:
		if item.lower() in location.lower():
			return True

	return False

# returns list of location, non_location entities from given entity dict with tags
# {'entity' : 'TAG'}
# where TAG can be any one from NE_LIST.
def separate_location_entities(entity_dict):
	'''
		Given entities Dict separetes 
		location and non-location entities
	'''
	location_entities = []
	non_location_entities = []
	for item in entity_dict:
		if entity_dict[item] in ['LOCATION', 'GPE']:
			location_entities.append(item)
		else:
			non_location_entities.append(item)
	return location_entities, non_location_entities

LE_COUNT = 0
# extracts all possible locations entities from given text
def extract_potential_locations(text):
	'''
		Given Text
		extract potential location entities
		input: text 
		outpu: le - location entities
			entities - all entities
	'''
	entities = bothTagger(text)
	#entities = nltkTagger(text)
	#entities = stanfordTagger(text)
	#entities_dict = entities_stanford
	#le, nle = separate_location_entities(all_entities)
	#le, nle = separate_location_entities(entities_nltk)
	le, nle = separate_location_entities(entities)
	c = 0
	#print(len(le), le)
	extra = []
	for ne in nle:
		for item in COMMON_WORDS_IN_LOCATION:
			if item.lower() in ne.lower():
				#le.append(ne)
				extra.append(ne)
				c += 1
	#print(c)
	global LE_COUNT
	LE_COUNT += c
	#print(LE_COUNT, extra)
	return le, entities


# returns crime locations
def extractCrimeLocations(text):
	'''
		Given text, extracts crime location entities
		input: text 
		output: CrimeLocations
	'''
	Locations, _ = extract_potential_locations(text)
	# Locations = fetchLocations(text)
	sentences = sent_tokenize(text)
	sentDict= {}
	
	for i, sent in enumerate(sentences):
		sent = sent.lower()
		# print(sent)
		words = word_tokenize(sent)
		stemWords = [PORTER.stem(word) for word in words]
		# if i <= 5:
		# 	num = 1
		# else:
		# 	num = i - 3
		div = 1/5.0
		if i/len(sentences) < div:
			num = 1
		elif i/len(sentences) >= div and i/len(sentences) < 2*div:
			num = 2
		elif i/len(sentences) > 2*div and i/len(sentences) <= 3*div:
			num = 3
		elif i/len(sentences) > 3*div and i/len(sentences) <= 4*div:
			num = 4
		else:
			num = 5

		if any(stemWord in CRIME_WORD_STEM_LIST for stemWord in stemWords):
			sentDict[sent] = ('crime', num)
		else:
			sentDict[sent] = ('non-crime', num)
		
	# print(sentDict)
	keyList=sorted(sentDict.keys())
	crimeLocations = {}
	crimeWordDistanceFromLocations = {}
	count = 0
	distanceCount = 0

	crimWordScore = returnCrimeWordScores()

	for loc in Locations:
		for i,sent in enumerate(sentDict):
			if loc.lower() in sent:
				# print(sent, " loc: ", loc)
				prepostion = sent.split(loc.lower())
				prefix = None
				suffix = None
				if len(prepostion) >= 2:
					prefix = prepostion[0].split()
					suffix = prepostion[1].split()
				elif len(prepostion) == 1:
					prefix = prepostion[0].split()
				if prefix:
					prefix = prefix[-1]
				if suffix:
					suffix = suffix[0]
				# print("prefix: ", prefix, "\tloc: ", loc, "\tsuffix: ", suffix)
				toAnalyzeSent = None
				if sentDict[sent][0] == 'crime':
					count += 1
					# crimeLocations.append(loc)
					if loc in crimeLocations.keys():
						crimeLocations[loc] += 1.0/sentDict[sent][1]
					else:
						crimeLocations[loc] = 1.0/sentDict[sent][1]

					
					toAnalyzeSent = sent



					# print(sent, " loc: ", loc)
					# break
				elif i != 0 and sentDict[keyList[i-1]][0] == 'crime':
					count += 1
					# crimeLocations.append(loc)
					if loc in crimeLocations.keys():
						crimeLocations[loc] += 1.0/sentDict[keyList[i-1]][1]
					else:
						crimeLocations[loc] = 1.0/sentDict[keyList[i-1]][1]
					# print(keyList[i-1], " loc: ", loc)
					# break

					toAnalyzeSent = keyList[i-1] + " " + sent

				elif i != len(sentDict) - 1 and sentDict[keyList[i+1]][0] == 'crime':
					count += 1
					# crimeLocations.append(loc)
					if loc in crimeLocations.keys():
						crimeLocations[loc] += 1.0/sentDict[keyList[i+1]][1]
					else:
						crimeLocations[loc] = 1.0/sentDict[keyList[i+1]][1]
					# print(keyList[i+1], " loc: ", loc)
					# break

					toAnalyzeSent = sent + " " + keyList[i+1]


				if toAnalyzeSent:
					# print(toAnalyzeSent, " loc: ", loc)
					# crime word and location distance storing
					tokens = toAnalyzeSent.split(loc)
					# print(len(tokens))
					# print("\n", " tokens: ", tokens)

					for i, token in enumerate(tokens):

						if i == 0:
							for word in token.split():
								# print(word)
								if PORTER.stem(word) in CRIME_WORD_STEM_LIST:
									# print(word)
									distanceCount += 1
									x = len(token.split(word)[1].split())

									wordScore = 1.0/crimWordScore[PORTER.stem(word)]
									
									if x != 0:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0/x + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0/x + wordScore
									else:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0 + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0 + wordScore
									# break

						elif i == len(tokens) - 1:
							for word in token.split():
								# print(word)
								if PORTER.stem(word) in CRIME_WORD_STEM_LIST:
									# print(word)
									distanceCount += 1
									wordScore = 1.0/crimWordScore[PORTER.stem(word)]
									x = len(token.split(word)[0].split())
									if x != 0:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0/x + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0/x + wordScore
									else:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0 + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0 + wordScore
									# break

						else:
							for word in token.split():
								# print(word)
								if PORTER.stem(word) in CRIME_WORD_STEM_LIST:
									# print(word)
									distanceCount += 2
									wordScore = 1.0/crimWordScore[PORTER.stem(word)]
									x = len(token.split(word)[0].split())
									y = len(token.split(word)[1].split())

									if x != 0:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0/x + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0/x + wordScore
									else:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0 + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0 + wordScore

									if y != 0:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0/y + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0/y + wordScore
									else:
										if loc in crimeWordDistanceFromLocations.keys():
											crimeWordDistanceFromLocations[loc] += 1.0 + wordScore
										else:
											crimeWordDistanceFromLocations[loc] = 1.0 + wordScore


	# print(Locations)
	if not crimeLocations:
		return []
	# print("hello")
	finalCrimeLocations = []
	finalCrimeLocations1 = []
	finalCrimeLocations2 = []
	# ===========================
	# print("count: ", count)
	NewCrimeLocationsSet1 = []
	NewTotalScore = 0
	totalScore = {}
	for loc in crimeLocations.keys():
		score = crimeLocations[loc]
		if loc in crimeWordDistanceFromLocations.keys():
			score += crimeWordDistanceFromLocations[loc]
		totalScore[loc] = score

	scoreDict = {}
	for loc in totalScore.keys():
		# print(loc, ": ", totalScore[loc])
		NewTotalScore += totalScore[loc]
		if totalScore[loc] in scoreDict:
			scoreDict[totalScore[loc]] += 1
		else:
			scoreDict[totalScore[loc]] = 1

	scoreCounter = Counter(scoreDict)
	scoreCounter = scoreCounter.most_common()
	temp = scoreCounter[0][1]

	NewThreshold1 = 0
	if temp > 1:
		for item in scoreCounter:
			if item[1] == temp:
				NewThreshold1 = item[0]
			else:
				break
	else:
		NewThreshold1 = NewTotalScore/count

	for loc in totalScore.keys():
		if totalScore[loc] >= NewThreshold1:
			NewCrimeLocationsSet1.append(loc)

	NewThreshold2 = NewTotalScore/count
	#print("New total score: ", NewTotalScore)
	#print("threshold: ", NewThreshold2)
	#print("count: ", count)

	NewCrimeLocationsSet2 = []
	for loc in totalScore:
		print(loc, " : ", totalScore[loc])
		if totalScore[loc] >= NewThreshold2:
			NewCrimeLocationsSet2.append(loc)

	NewCrimeLocationsSet1 = set(NewCrimeLocationsSet1)
	NewCrimeLocationsSet2 = set(NewCrimeLocationsSet2)

	return NewCrimeLocationsSet2


def returnmatchescount(prediction, original):
	total = []
	for item in original:
		if item in prediction:
			total.append(item)
		tokens = item.split()
		for tok in tokens:
			if tok in prediction:
				total.append(item)
			for l in prediction:
				if tok in l:
					total.append(item)

	# print(total)
	return len(set(total)), len(original) - len(set(total))


if __name__ == '__main__':
	
	query = 'SELECT * from NewsArticles as N, CrimeNewsDetails as C Where N.NewsArticleID = C.NewsArticleID'
	data = fetch_query_output(query)
	total_common = 0
	total_prediction = 0
	total_original = 0
	for i, article in enumerate(data):
		print("processing ", i+1, " article id: ", article[0])
		text = article[1] + " " + article[2]
		original = article[14].split('|')
		prediction = extractCrimeLocations(text)
		#print(original,'\n',  prediction)
		#print(len(original)-1, ' ', len(prediction))
		total_original += len(original)-1
		total_prediction += len(prediction)
		x,y = returnmatchescount(prediction, original)
		total_common += x

	print("totalcommon: ", total_common)
	print("total originals: ", total_original)
	print("total predictions: ", total_prediction)
