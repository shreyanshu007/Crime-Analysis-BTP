#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python

# required modules
import nltk
import string
import gensim
import pymysql
import numpy as np
from nltk.stem.porter import *
from nltk.corpus import wordnet
from nltk.stem import PorterStemmer
from gensim.utils import simple_preprocess
from gensim.parsing.preprocessing import STOPWORDS
from nltk.stem import WordNetLemmatizer, SnowballStemmer



# Required text file "CrimePhrase.txt"




translator = str.maketrans('', '', string.punctuation)
STEM = PorterStemmer()
stemmer = SnowballStemmer("english")


# Classes

# NOT A CRIME
class0 = 0		

# Harrasment
class1 = ['harrasment', 'persecution', 'harrying', 'pestering', 'badgering', 'intimidation', 'bother', 'annoyance', 'aggravation', 'irritation', 'pressure', 'pressurization', 'force', 'coercion', 'molestation', 'hassle', 'badassery', 'bedevilment']

# Molest
class2 = ['molest', 'abuser', 'violate' ,'attack' ,'hurt' ,'harm' ,'injure' ,'maul' ,'grope' ,'paw' ,'ravish' ]

# Rape	
class3 = ['gang-rape', 'rapist','gangraped','Rape','Defilement']

# Assault
class4 = ['assassin','assailant','blackmailer','abuser','goons','Assault','Battery','Attack','Beating','Hit']

# Murder
class5 = ['murderer','assassin','Death','Died','shot','Homicide','Murder','Killing','Slaughter','Gunshot','murdered','killed','stabbed']	

# Scucide
class6 = ['Death','Died','shot','Suicide','Gunshot']	

# Accident
class7 = ['Death','Died','incident','Accident','Collision','Colliding','Impact','Crash','Hit']	

# Kidanapping	
class8 = ['trafficker','kidnapper','Kidnapping','Abduction']

# Robbery & Theft
class9 = ['thief','hijacker','smuggler','burglar','embezzler','forger','looter','mugger','robber','Snatching','Larceny','Thievery','Theft','Robbery','Burglary','Mugging','Embezzlement','Fraud','Defalcation','Stealing','Forgery','Conspiracy']	

# Terrorism
class10 = ['arsonist','bomber','Death','Died','shot','Attack','Terrorism','Arson','Incendiarism','Torching','Gunshot','blasts']	


class1 = [STEM.stem(x.lower()) for x in class1]
class2 = [STEM.stem(x.lower()) for x in class2]
class3 = [STEM.stem(x.lower()) for x in class3]
class4 = [STEM.stem(x.lower()) for x in class4]
class5 = [STEM.stem(x.lower()) for x in class5]
class6 = [STEM.stem(x.lower()) for x in class6]
class7 = [STEM.stem(x.lower()) for x in class7]
class8 = [STEM.stem(x.lower()) for x in class8]
class9 = [STEM.stem(x.lower()) for x in class9]
class10 = [STEM.stem(x.lower()) for x in class10]


classList = [class1,class2,class3,class4,class5,class6,class7,class8,class9,class10]
crimeLable = ['Harrasment', 'Molest', 'Rape', 'Assault', 'Murder', 'Suicide', 'Accident', 'Kidnapping', 'Robbery', 'Terrorism']




CrimePhrasesDict = {}
with open("/home/2016CSB1059/BTP/CrimeClassification/CrimePhrases.txt", "r+") as file:
	for word in file.read().split('\n'):
		processed_word = STEM.stem(word.lower())
		for syn in wordnet.synsets(word):
			if processed_word == STEM.stem(syn.lemmas()[0].name()):
				if processed_word in CrimePhrasesDict.keys():
					CrimePhrasesDict[processed_word] += len(syn.definition().split(';'))
				else:
					CrimePhrasesDict[processed_word] = 1 + len(syn.definition().split(';'))




def extractCrimeWord(article, returnOnlyLabels=False):

	class_value = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

	'''title = article[1]
	body = article[2]

	text = title + body'''
	text = article

	# Title
	for phrase in text.translate(translator).lower().split():
		count = 0
		for temp_class in classList:
			if STEM.stem(phrase) in temp_class:
				class_value[count] += 1
			count += 1

	label = crimeLable[class_value.index(max(class_value))]
	# print(class_value)

	if returnOnlyLabels:
		final_list = []
		for i,val in enumerate(class_value):
			if val:
				final_list.append(crimeLable[i])

		return final_list

	# return crimeLable, class_value
	return label, class_value.index(max(class_value))

def classifyCrime(article):

	crime = 'crime'
	non_crime = 'non-crime'

	title = article[1]
	body = article[2]
	label = article[7]
	new_label_title = non_crime
	new_label_text = non_crime
	new_label = non_crime
	crime_word_list = []
	crime_count = 0.0

	if not title or not body:
		return 'non-crime'

	# Title
	for phrase in title.translate(translator).lower().split():
		if STEM.stem(phrase) in CrimePhrasesDict.keys():
			new_label_title = crime
			crime_count += 1.0/int(CrimePhrasesDict[STEM.stem(phrase)])

	# Body
	for phrase in body.translate(translator).lower().split():
		if STEM.stem(phrase) in CrimePhrasesDict.keys():
			new_label_text = crime
			crime_count += 1.0/int(CrimePhrasesDict[STEM.stem(phrase)])

	new_label = new_label_text
	if new_label_title == non_crime and new_label_text == crime:
		if crime_count > 1.1:
			new_label = crime
		else:
			new_label = non_crime

	return new_label

