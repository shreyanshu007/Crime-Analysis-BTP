#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python

import pymysql
import nltk
from nltk.corpus import wordnet
from operator import add
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer

tokenizer = RegexpTokenizer(r'\w+')


# list of crime words. 
CRIME_WORDS = ['assault', 'suicide', 'terrorism', 'kidnap', 'murder', 'rape', 'robbery', 'rob', 'kill'] + ['murder','rape','burglary','theft','harass','hijack','kidnap','robbery','snatching','lynching']
CRIME_WORDS = list(set(CRIME_WORDS))
STEM = PorterStemmer()
NER_POS_TAG_SCORE = {}

# function to check the wup similarity between the words.
# using the depth concept of the words and the LCS
def similarity_score(word1, word2):

	# use of synsets for synonyms calculation.
	word1 = wordnet.synsets(word1)
	word2 = wordnet.synsets(word2)

	if word1 and word2:
		
		score = 0
		x1 = word1[0].wup_similarity(word2[0])
		x2 = word1[0].path_similarity(word2[0])
		
		if x1:
			score += x1
		if x2:
			score += x2
		if word1[0].pos() == word2[0].pos():
			x3 = word1[0].lch_similarity(word2[0])
			norm1 = word1[0].lch_similarity(word1[0])
			if x3 and norm1 and norm1 != 0:
				score += x3/norm1
		
		return score/3.0
	else:
		return 0


# Returns the CRIME Words Score on the basis of similarity
# output: Dictionary : denoting collection of words and their respective scores.
def return_dictionary():
	
	Synonyms = []
	for word in CRIME_WORDS:
		temp = wordnet.synsets(word)
		for t in temp:
			for i in t.lemmas():
				if similarity_score(word, i.name()) > 0.7:
					Synonyms.append(i.name())

	# list of synonyms of CRIME WORDS
	Synonyms = list(set(Synonyms))
	Synonyms_score = {}
	for syn in Synonyms:
		if syn in CRIME_WORDS:
			Synonyms_score[syn] = 5
		else:
			Synonyms_score[syn] = 0


	for key in Synonyms_score:
		if Synonyms_score[key] == 0:
			value = 0
			count = 0
			word1 = wordnet.synsets(key)
			for word in CRIME_WORDS:
				word2 = wordnet.synsets(word)
				if word1 and word2:
					# print(word1[0])
					# print(wordnet.synsets.getmembers(OptionParser, predicate=inspect.ismethod))
					# print(word2[0].pos())
					sim = 0
					x1 = word1[0].wup_similarity(word2[0])
					x2 = word1[0].path_similarity(word2[0])
					
					if x1:
						sim += x1
					if x2:
						sim += x2
					if word1[0].pos() == word2[0].pos():
						x3 = word1[0].lch_similarity(word2[0])
						norm1 = word1[0].lch_similarity(word1[0])
						# norm2 = word2[0].lch_similarity(word2[0])

						# print(x3)
						sim += x3/norm1

					sim /= 3.0


					if sim and wordnet.synsets(word)[0].lemmas()[0].name() in Synonyms_score.keys():
						value += (sim*Synonyms_score[wordnet.synsets(word)[0].lemmas()[0].name()])
						count +=1

			if count != 0:
				Synonyms_score[key] = value/count

	return Synonyms_score


# function to check whether given article is crime article or not a crime article based on the score assigned by this function to that article.
# input
# article: article text.
# output
# final_score : returns the final crime score of that article.....
def crime_check(tupleSent, article='', stopwords=['.']):

	Synonyms_score, total = tupleSent
	article = tokenizer.tokenize(article)
	# total_words = nltk.word_tokenize(article)
	total_words = list(set(article))

	words = [word for word in total_words if word not in stopwords]

	# print("total words: ", len(words))
	# sim_score = [similarity_score('', word_from_text) for word_from_text in words]
	contributing_words = []
	sim_score1 = 0
	sim_score2 = 0
	count = 0
	for word1 in Synonyms_score:
		for word2 in words:
			temp = similarity_score(word1, word2)
			levDist = nltk.edit_distance(word1, word2)
			reqDist = (2 * len(word1) * len(word2)) / (len(word1) + len(word2))
			# reqDist = max(len(word1), len(word2))
			if temp > .9 and levDist < reqDist:
				# print(word1, " -> ", word2)
				# print(levDist, " ------ ", reqDist)
				sim_score1 += (Synonyms_score[word1]*temp)
				contributing_words.append(word2)
				# count += 1

			elif STEM.stem(word1) == STEM.stem(word2) and word1 in CRIME_WORDS:
				# print(word1, " : ", word2)
				sim_score2 += Synonyms_score[word1]
				contributing_words.append(word2)
				# count += 1

	# print(sim_score,  " ", count)
	# final_Score = 0
	# if count != 0:
	final_Score = sim_score1 ## divide by count
	final_Score += sim_score2
	# print("Contributing Words: ", contributing_words)
	return final_Score



# function to check the type of crime article.
def crime_type(article=''):

	type_of_crime = []

	aritcle_words = nltk.word_tokenize(article)
	stem_articles = [STEM.stem(w.lower()) for w in aritcle_words]
	# print(stem_articles)
	# print(STEM.stem('robbery'))

	for word in CRIME_WORDS:
		if STEM.stem(word.lower()) in stem_articles:
			type_of_crime.append(word)

	for word1 in CRIME_WORDS:
		for word2 in aritcle_words:
			if similarity_score(word1.lower(),word2.lower()) > 0.9:
				type_of_crime.append(word1)


	# print("\nType of Crime: ", set(type_of_crime))
	return list(set(type_of_crime))




def transfer(articleID=0):

	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT *  FROM NewsArticles WHERE NewsType IS NOT NULL"
	text = None
	try:
		with connection:
			db = connection.cursor()
			db.execute(sql,)
			# result = 
			text = db.fetchall()
			# text = result[0][2] + " " + result[0][3]
			connection.commit()
		

	except Exception as e:
		# print("exception ", e)
		connection.rollback()
	finally:
		# print("finally")
		db.close()
		connection.close()

	return text



# function that extracts location from the given text
def location_extraction(text, stat_dict):

	locations = []
	sentences = nltk.sent_tokenize(text)
	words = []
	for sent in sentences:
		words = words + nltk.word_tokenize(sent)
	pos_tag_output = nltk.pos_tag(words)

	chunks = nltk.ne_chunk(nltk.pos_tag(words))
	pre = None
	# print(chunks)
	for chunk in chunks:
		flag = True
		if hasattr(chunk, 'label'):

			if pre and hasattr(pre, 'label'):
				m = 0
				max_label = None
				for item in stat_dict.keys():
					if pre[0][1] in stat_dict[item].keys():
						temp = stat_dict[item][pre[0][1]]
						if temp > m:
							m = temp
							max_label = item
				if max_label in ['GSP', 'GPE', 'LOCATION']:
					flag = False
					locations.append(' '.join(c[0] for c in chunk))

			elif pre:
				m = 0
				max_label = None
				for item in stat_dict.keys():
					if pre[1] in stat_dict[item].keys():
						temp = stat_dict[item][pre[1]]
						if temp > m:
							m = temp
							max_label = item
				if max_label in ['GSP', 'GPE', 'LOCATION']:
					flag = False
					locations.append(' '.join(c[0] for c in chunk))

			if flag and chunk.label() == 'GSP' or chunk.label() == 'GPE' or chunk.label() == 'LOCATION':
				# print(' '.join(c[0] for c in chunk), " ------ prev label: ", pre.label())
				# print(' '.join(c[0] for c in chunk), " ------ label: ", chunk.label())
				# print("previous chunk -----> : ", pre, "\t current chunk -----> : ", chunk)
				locations.append(' '.join(c[0] for c in chunk))

		pre = chunk

	return locations



# function to analyse the NER entities and pos_tags
def analyse_text(text):
	sentences = nltk.sent_tokenize(text)
	words = []
	for sent in sentences:
		words = words + nltk.word_tokenize(sent)
	pos_tag_output = nltk.pos_tag(words)

	chunks = nltk.ne_chunk(nltk.pos_tag(words))
	pre = None
	# print(chunks)
	for chunk in chunks:
		if hasattr(chunk, 'label'):
			if chunk.label() not in NER_POS_TAG_SCORE.keys():
				NER_POS_TAG_SCORE[chunk.label()] = {}

			if pre and hasattr(pre, 'label'):
				if pre[0][1] not in NER_POS_TAG_SCORE[chunk.label()].keys():
					NER_POS_TAG_SCORE[chunk.label()][pre[0][1]] = 1
				else:
					NER_POS_TAG_SCORE[chunk.label()][pre[0][1]] += 1

			elif pre:
				# print(pre[1], "\n")
				if pre[1] not in NER_POS_TAG_SCORE[chunk.label()].keys():
					NER_POS_TAG_SCORE[chunk.label()][pre[1]] = 1
				else:
					NER_POS_TAG_SCORE[chunk.label()][pre[1]] += 1
		pre = chunk

	# print("DICT: ", NER_POS_TAG_SCORE)


# article = 'Deepika Amin accuses Alok Nath of harassment, calls him a drunkard who harasses women. Allegations against Alok Nath are piling up. After Vinta Nanda and Sandhya Mridul, actor Deepika Amin has come forward with her tale of harassment at the hands of the said actor.  Taking to Twitter, Deepika wrote how during an outdoor shoot of a telefilm, early in her career, Alok tried to barge into her room. She wrote: “Everyone in the industry knows that #AlokNath is an obnoxious drunkard who harasses women. Years ago on a telefilm outdoor shoot he tried to barge into my room. He slobbered over women, drunk and created a scene. The unit rallied around me and made sure I was safe. #metoo.”  Everyone in the industry knows that #AlokNath is an obnoxious drunkard who harasses women. Years ago on a telefilm outdoor shoot he tried to barge into my room. He slobbered over women, drunk and created a scene. The unit rallied around me and made sure I was safe. #metoo — Deepika Amin (@amindeepika) October 10, 2018  She added that her unit then protected her from him and hence she felt safe. Deepika further wrote on Facebook that she was quite young at that time but remembers “vividly how horrible he was”. She goes on to elaborate how she again worked with him recently in the film Sonu Ke Titu Ki Sweety but he was sober on the sets.  She wrote: “Everyone in the industry knows that #AlokNath is an obnoxious drunkard who harasses women. Years ago on a telefilm outdoor shoot he tried to barge into my room. He slobbered over women, drunk and created a scene. The unit rallied around me and made sure I was safe. I was quite young but I still remember vividly how horrible he was. But recently on the shoot of Sonu Ke Titu ki Sweety he was quiet and subdued . Maybe he has changed? Maybe because the director Luv Ranjan made it clear he wouldn’t tolerate bad behaviour. But after reading Vinta Nanda’s heartbreaking account I felt I had to support her. BELIEVE WOMEN . They have everything to lose by speaking out. #IbelieveyouVintaNanda #metoo #Timesup.”  Deepika wrote this as she shared Vinta’s Facebook post.  On October 8, writer-director Vinta Nanda, known for her TV series Tara, wrote a long post detailing how she was raped 19 years ago by Alok while she was on her way back from a party. On Wednesday, actor Sandhya shared her story from her early days as an actor when she was attacked by a drunk Alok while on an outdoor shoot.  Follow @htshowbiz for more  First Published: Oct 11, 2018 12:44 IST | 2018-10-11 12:44:42 | https://www.hindustantimes.com/bollywood/deepika-amin-accuses-alok-nath-of-harassment-calls-him-a-drunkard-who-harasses-women/story-EKV94MD2lc2eSuECWVvaVL.html'

if __name__ == '__main__':
	

	Synonyms_score = return_dictionary()
	total = 0
	for key in Synonyms_score:
		total += Synonyms_score[key]

	stopWords = set(stopwords.words('english'))

	NewsData = transfer()
	
	predActualCrimeAsCrime = 0
	predActualNonCrimeAsCrime = 0
	predActualCrimeAsNonCrime = 0
	predActualNonCrimeAsNonCrime = 0

	actualCrimeNumbers = 0
	actualNonCrimeNumbers = 0
	totalNews = 0
	count = 0
	for news in NewsData:

		totalNews += 1
		print("News No.: ", totalNews)
		newsText = news[1] + news[2]
		newsText = newsText.replace('.', '. ')
		print(newsText)
		fs = crime_check((Synonyms_score, total), newsText, stopWords)
		# print("score: ", fs)
		if fs >= 5.0 and news[7] == 'crime':
			print("crime: ", fs)	
			actualCrimeNumbers += 1
			predActualCrimeAsCrime += 1

		elif fs < 5.0 and news[7] == 'crime':
			print("crime: ", fs)
			actualCrimeNumbers += 1
			predActualCrimeAsNonCrime += 1

		elif fs >= 5.0 and news[7] == 'non-crime':
			print("non-crime: ", fs)
			actualNonCrimeNumbers += 1
			predActualNonCrimeAsCrime += 1

		elif fs < 5.0 and news[7] == 'non-crime':
			print("non-crime: ", fs)
			actualNonCrimeNumbers += 1
			predActualNonCrimeAsNonCrime += 1

		count += 1
		# if count > 200:
		# 	break

		print("\n\n")


	print("Actual Crime News: ", actualCrimeNumbers)
	print("ACtual NOn Crime News: ", actualNonCrimeNumbers)
	print("Crime as Crime: ", predActualCrimeAsCrime)
	print("Crime as Non Crime: ", predActualCrimeAsNonCrime)
	print("NOn crime as Crime: ", predActualNonCrimeAsCrime)
	print("Non crime as Non crime: ", predActualNonCrimeAsNonCrime)



	# for i in range(101,181101):
	# 	if (i-100)%1000 == 0:
	# 		x = i-100
	# 		print("%s new completed" % x)
	# 	text = transfer(i)
	# 	fs = 0
	# 	if text:
	# 		fs = crime_check((Synonyms_score, total), text, stopWords)
	# 		print("\n\nfinal score: ", fs)
	# 		if fs > 0.03:
	# 			print("\nCrime News: \n\n", text)
	# 			crime_type(text)