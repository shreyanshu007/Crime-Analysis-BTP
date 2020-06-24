# previous methods and some changes in the duplicate codes.....

# some modules imported earlier
import spacy
from spacy import displacy
from collections import Counter
import en_core_web_sm
from pprint import pprint
from nltk import RegexpParser
from nltk import Tree
import pandas as pd
from nltk.corpus import stopwords
from nltk.probability import FreqDist
import nltk
import math

class DuplicateDetection(object):

	# function for debugging and checking dataset
	def returnSimilarityScore(self, articleText, crime_type, location_entities, person_entities, organization_entities):

		if type(self.crime_type) != list:
			self.crime_type = [self.crime_type]

		if type(self.crime_type) != list:
			crime_type = [crime_type]

		similar_crime_type = list(set(self.crime_type).intersection(set(crime_type)))

		self.entities = self.location_entities + self.organization_entities + self.person_entities
		entities = location_entities + organization_entities + person_entities

		similar_entities = list(set(self.entities).intersection(set(entities)))

		# print("crime type: ", similar_crime_type)
		# print("entities: ", similar_entities)

		if similar_entities:
			# print("crime type: ", similar_crime_type)
			# print("entities: ", similar_entities)

			file.write(str(GLOBAL_COUNT[0]) + "|" + str(LOCAL_COUNT[0]) + "\n")
			file.write('=========================================================================================================\n')
			file.write(GLOBAL_COUNT[1].replace('\n', ' ') + "\n" + GLOBAL_COUNT[2].replace('\n', ' ') + "\n")
			file.write('----------------------------------------Compared With ---------------------------------------------------\n')
			file.write(LOCAL_COUNT[1].replace('\n', ' ') + "\n" + LOCAL_COUNT[2].replace('\n', ' ') + "\n")
			file.write('---------------------------------------- Results in -----------------------------------------------------\n')
			file.write("Similar Crime Type: \n" + str(similar_crime_type) + "\n")
			file.write("Similar Entities: \n" + str(similar_entities) + "\n")
			file.write('=========================================================================================================\n\n\n')


def Preprocessing(text):
    '''
        Function for pre-processing of text.
	input: text - text to process
	output: processed words list(text)
    '''
    eng_stopwords = stopwords.words("english")
    words_in_text = nltk.word_tokenize(text)
    text = [word.lower() for word in words_in_text if word not in eng_stopwords]

    return text


def tf(text, wordset):
    '''
        function to calculate term frequency of given text.
	input: text - list of word returned from Preprocessing
	output: text_tf_dict - tf score of words
    '''
    freq_text = FreqDist(text)
    text_length = len(text)
    text_tf_dict = dict.fromkeys(wordset, 0)
    for word in text:
        text_tf_dict[word] = freq_text[word]/text_length

    return text_tf_dict


def idf(text1, text2, wordset):
    '''
        Function to calculate inverse document frequency of given text.
	input: text1, text2 - lists of words returned from Prepeocssing function
		for doc1 and doc2 respectively
	       wordset - union of words in doc1 and doc2
	output: idf_dict - idf score of text
    '''
    idf_dict = dict.fromkeys(wordset, 0)
    no_of_docs = 2
    for word in idf_dict.keys():
        if word in text1:
            idf_dict[word] += 1

        if word in text2:
            idf_dict[word] += 1

    for word, val in idf_dict.items():
        idf_dict[word] = 1 + math.log(no_of_docs/(float(val)))

    return idf_dict


def tf_idf(text, wordset, tf_dict, idf_dict):
    '''
        function to calculate the tf-idf value for a given documet.
	input: 	text - list of words 
		wordset - union of words in doc1 and doc2
		tf_dict - tf score dict of doc1
		idf_dict - idf score dict
    '''
    text_tf_idf_dict = dict.fromkeys(wordset, 0)
    for word in text:
        text_tf_idf_dict[word] = tf_dict[word] * idf_dict[word]

    return text_tf_idf_dict


def distance_computation(tf_idf1, tf_idf2):
    '''
        function to calculate the distance between two text.
	input: tf_idf1/2 - tf scores of both docs
	output: distance score
    '''
    v1 = list(tf_idf1.values())
    v2 = list(tf_idf2.values())

    return 1 - nltk.cluster.cosine_distance(v1,v2)


def similarity_score(document1, document2):
    '''
        function to calculate the similarity between given two documents.
	input: doc1 and doc2
	output: similarity_score - score of similarity of given docs.
    '''

    text1 = Preprocessing(document1)
    text2 = Preprocessing(document2)

    wordset = set(text1).union(set(text2))

    tf1 = tf(text1,wordset)
    tf2 = tf(text2,wordset)

    doc_idf = idf(text1,text2,wordset)

    tf_idf1 = tf_idf(text1,wordset,tf1,doc_idf)
    tf_idf2 = tf_idf(text2,wordset,tf2,doc_idf)

    similarity = distance_computation(tf_idf1, tf_idf2)

    return similarity




'''nlp = en_core_web_sm.load()


# function returning set of entities from a given text
def entities(text):

	doc = nlp(text)
	entitiesList = {}
	

	# pprint([(X.text, X.label_) for X in doc.ents])
	for item in doc.ents:
		if item.label_ in NER_LIST:
			if item.text in entitiesList.keys():
				entitiesList[item.text].append(item.label_)
			else:
				entitiesList[item.text] = [item.label_]

	sentences = sent_tokenize(text)
	for sent in sentences:
		nltkTagger = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)))
		for chunk in nltkTagger:
			if hasattr(chunk, 'label') and chunk.label() in ['GPE', 'PERSON', 'LOCATION', 'ORGANIZATION']:
				ent = ' '.join(c[0] for c in chunk)
				if ent in entitiesList.keys():
					entitiesList[ent].append(chunk.label())
				else:
					entitiesList[ent] = [chunk.label()]


	for entity in entitiesList:
		entitiesList[entity] = max(entitiesList[entity],key=entitiesList[entity].count)

	print(entitiesList)
	return entitiesList


def stanfordTagger(chunkList):

	chunkList = word_tokenize(chunkList)
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

				entities[entity] = total[0][1]
	# print(entities)
	return entities


'''
