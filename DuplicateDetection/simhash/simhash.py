#!/home/2016CSB1059/Crime_analysis/SummerProject/bin/python
# -*- coding: utf-8 -*-

import re
from hashlib import md5, sha224
import sys
import os
f = os.path.dirname(os.path.abspath(__file__))
sys.path.append(f)
import LocationExtraction.locationExtraction as le
import CrimeClassification.MainCrimeClassifier as fileCrimeClassify

class Token:

    def __init__(self, hash_list, weight):
        self.hash_list = hash_list
        self.weight = weight

def tokenize(doc):
    """
    Lower case, remove punctuation and split in spaces
    """
    text = doc
    doc = doc.lower()
    doc = re.sub('[,;]', ' ', doc)
    doc = re.split('\s+', doc)
    doc = sorted(list(filter(None, doc)))
    ent = le.stanfordTagger(text)
    print(ent)
    l = []
    for item in ent:
        if ent[item] in ['LOCATION', 'GPE','PERSON']:
            l.append(item)
    ent = l#ent = sorted(list(le.stanfordTagger(text).keys()))
    #print(ent)
    #ent = [e.lower() for e in ent]
    crime_type = fileCrimeClassify.extractCrimeWord(text, returnOnlyLabels=True)
    crime_type = [c.lower() for c in crime_type]
    #print(crime_type + ent)
    #print(doc)
    return doc, ent + crime_type

def md5Hash(token):
    x1 = int(sha224(token[0].encode('utf-8')).hexdigest(), 16)
    x2 = int(sha224(token[1].encode('utf-8')).hexdigest(), 16)
    x3 = int(sha224(token[2].encode('utf-8')).hexdigest(), 16)
    h = bin(x2)
    return h[2:]

def hash_threshold(token_dict, fp_len):
    """
    Iterate through the token dictionary multiply the hash lists with the weights
    and apply the binary threshold
    """
    sum_hash = [0] * fp_len
    for _, token in token_dict.items():
        sum_hash = [ x + token.weight * y for x, y in zip(sum_hash, token.hash_list)]

    # apply binary threshold
    for i, ft in enumerate(sum_hash):
        if ft > 0:
            sum_hash[i] = 1
        else:
            sum_hash[i] = 0
    return sum_hash

def binconv(fp, fp_len):
    """
    Converts 0 to -1 in the tokens' hashes to facilitate
    merging of the tokens' hashes later on.
    input  : 1001...1
    output : [1,-1,-1, 1, ... , 1]
    """
    vec = [1] * fp_len
    #print(fp, len(fp))
    for indx, b in enumerate(fp):
        if indx == 224:
            break
        if b == '0':
            vec[indx] = -1
    return vec


def calc_weights(terms, ent, fp_len):
    """
    Calculates the weight of each one of the tokens. In this implementation
    these weights are equal to the term frequency within the document.

    :param tokens: A list of all the tokens (words) within the document
    :fp_len: The length of the Simhash values
    return dictionary "my_term": Token([-1,1,-1,1,..,-1], 5)
    """
    term_dict = {}
    length = len(terms)
    for i, term in enumerate(terms):
        # get weights
        arguments = [terms[(i-1)%length], term, terms[(i+1)%length]]
        if term not in term_dict:
            fp_hash = md5Hash(arguments).zfill(fp_len)
            fp_hash_list = binconv(fp_hash, fp_len)
            token = None
            #if term in ent:
            #    token = Token(fp_hash_list, 2)
            #else:
            token = Token(fp_hash_list, 0)
            term_dict[term] = token
        #if term in ent:
        #    term_dict[term].weight += 1
        #else:
        term_dict[term].weight += 1
    return term_dict

def simhash(doc, fp_len=224):
    """
    :param doc: The document we want to generate the Simhash value
    :fp_len: The number of bits we want our hash to be consisted of.
                Since we are hashing each token of the document using
                md5 (which produces a 128 bit hash value) then this
                variable fp_len should be 128. Feel free to change
                this value if you use a different hash function for
                your tokens.
    :return The Simhash value of a document ex. '0000100001110'
    """
    tokens, ent = tokenize(doc)
    token_dict = calc_weights(ent, ent, fp_len)
    fp_hash_list = hash_threshold(token_dict, fp_len)
    fp_hast_str =  ''.join(str(v) for v in fp_hash_list)
    return fp_hast_str


# Return the Hamming distance between string1 and string2.
# string1 and string2 should be the same length.
def hamming_distance(string1, string2): 
    # Start with a distance of zero, and count up
    distance = 0
    # Loop over the indices of the string
    L = len(string1)
    for i in range(L):
        # Add 1 to the distance if these two characters are not equal
        if string1[i] != string2[i]:
            distance += 1
    # Return the final count of differences
    return distance

def returnmatchescount(list1, list2):
	total = []
	for item in list1:
		if item in list2:
			total.append(item)
		#print(item)
		tokens = item.split()
		for tok in tokens:
			if tok in list2:
				total.append(item)
			for l in list2:
				if tok in l:
					total.append(item)

	# print(total)
	return len(set(total))


if __name__ == '__main__':
	pass
