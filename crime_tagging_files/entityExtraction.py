#!/home/2016CSB1059/project_env/bin/python

import sys
'''
    Location extraction file.
    This file extracts the possible crime location for any given crime article.
'''
# import CityList
import nltk
# import regex as re
# import CrimeCheck
# import ArticleSimilarityCheck
import numpy as np
from nltk.corpus import wordnet 
from copy import deepcopy
from CrimeCheck_v2 import crime_type

'''
    This module is used to make a city list from given input Excel or txt file.
'''

import xlrd

## this function takes input as the names of the text and excel file and returns a list containing the names in the file.
def ReturnListFromFile(textfile = '', excelfile = '/home/2016CSB1059/Crime_analysis/SummerProject/bin/list_of_cities_and_towns_in_india-834j.xls'):

    workbook = xlrd.open_workbook(excelfile)

    worksheet = workbook.sheet_by_index(0)

    city_data = []

    for row_index in range(1, worksheet.nrows): # skip heading row
        col1, col2 = worksheet.row_values(row_index, end_colx=2)

        if col2.lower() not in city_data:
            city_data.append(col2.lower())

    with open("/home/2016CSB1059/Crime_analysis/SummerProject/bin/citiesname.txt",'r') as file:
        for line in file:
            if line.strip().lower() not in city_data:
                city_data.append(line.strip().lower())

    with open("/home/2016CSB1059/Crime_analysis/SummerProject/bin/citytownvillage.txt",'r') as file:
        for line in file:
            if line.strip().lower() not in city_data:
                city_data.append(line.strip().lower())

    with open("/home/2016CSB1059/Crime_analysis/SummerProject/bin/state.txt",'r') as file:
        for line in file:
            if line.strip().lower() not in city_data:
                city_data.append(line.strip().lower())


    return city_data

## Some important variables used in this program.
CITY_LIST = ReturnListFromFile()
# print(CITY_LIST)
for i in range(len(CITY_LIST)):
    
    if '\t' in CITY_LIST[i]:
        CITY_LIST[i] = CITY_LIST[i].replace('\t', ' ')

    if '(' in CITY_LIST[i]:

        item = CITY_LIST[i]
        index1 = CITY_LIST[i].find('(')
        index2 = CITY_LIST[i].find(')')
        CITY_LIST[i] = CITY_LIST[i][0:index1-2]
        CITY_LIST.append(item[index1+1:index2])

    if '[' in CITY_LIST[i]:

        item = CITY_LIST[i]
        index1 = CITY_LIST[i].find('[')
        index2 = CITY_LIST[i].find(']')
        CITY_LIST[i] = CITY_LIST[i][0:index1-2]
        CITY_LIST.append(item[index1+1:index2])




# print(CITY_LIST)

PREPOSITION_LIST = ['in','near','from','around','at','outer','south','east','west','north']

LOCATION_TAGS = ['bhavan','pradesh','ashram','nagar','pur','vihar','chowk','road','area','sector','north','east','west','south','garden','park','camp','central','crossing','garh','ganj', 'bad']

PORTER = nltk.PorterStemmer()

CRIME_WORD_LIST = ['murder','rape', 'bullying','burglary','theft','fraud','harass','hijack','kidnap','kill','robbery','snatching','lynching','shoot']
crime_list = deepcopy(CRIME_WORD_LIST)
for crime_word in crime_list:

    synonyms = wordnet.synsets(crime_word)
    # print("\n", crime_word, ": ")
    for syn in synonyms:
        for i in syn.lemmas():
            # print(i.name())
            CRIME_WORD_LIST.append(i.name())

CRIME_WORD_LIST = list(set(CRIME_WORD_LIST))
# print(CRIME_WORD_LIST)
CRIME_WORD_STEM_LIST = [PORTER.stem(crime_word) for crime_word in CRIME_WORD_LIST]









'''
    The function returns the entities from the News Article.
    The entities consist following things:
        Names of the people involved in the news.
        Crime Locations.
        Non-Crime Locations.
        Crime word list - Crimes involved.
'''
def return_entities(Text):

    Text = Text.replace('.', '. ')
    Locations = []
    Entities = []
    crime_word_list = []
    names = []

    sentences = nltk.sent_tokenize(Text)
    
    '''
        Entities Extraction.....
    '''
    # crime_word_list = crime_type(Text)
    for sent in sentences:
        # print(sent, "\n")
        words = nltk.word_tokenize(sent.lower())
        for word in words:
            if PORTER.stem(word) in CRIME_WORD_STEM_LIST:
                crime_word_list.append(word)
	
        chunks = nltk.ne_chunk(nltk.pos_tag(nltk.word_tokenize(sent)))
        # print(chunks[0], chunks[1])
        length = len(chunks)
        for i in range(length):
            curr = chunks[i]
            if i == 0 and i+1 < len(chunks):
                prev = None
                Next = chunks[i+1]

            elif i == length-1:
                prev = chunks[i-1]
                Next = None

            else:
                prev = chunks[i-1]
                Next = chunks[i+1]

            if curr and hasattr(curr, 'label'):
                # print(curr)
                # print(Next)
                if prev and Next and hasattr(prev, 'label') and hasattr(Next, 'label'):# and prev.label() in ['GPE', 'PERSON', 'LOCATION'] and Next.label() in ['GPE', 'PERSON', 'LOCATION']:
                    item = ' '.join(c[0] for c in prev) + ' ' + ' '.join(c[0] for c in curr) + ' ' + ' '.join(c[0] for c in Next)
                    # print(item)
                    Entities.append(item)

                elif prev and hasattr(prev, 'label'):# and prev.label() in ['GPE', 'PERSON', 'LOCATION']:
                    item = ' '.join(c[0] for c in prev) + ' ' + ' '.join(c[0] for c in curr)
                    # print(item)
                    Entities.append(item)

                elif Next and hasattr(Next, 'label'):# and Next.label() in ['GPE', 'PERSON', 'LOCATION']:
                    item = ' '.join(c[0] for c in curr) + ' ' + ' '.join(c[0] for c in Next)
                    # print(item)
                    Entities.append(item)

                else:
                    item = ' '.join(c[0] for c in curr)
                    # print(item)
                    Entities.append(item)
    

    '''
        Location Extraction from these Entities.....
    '''
    for entity in set(Entities):
        
        if entity.lower() in CITY_LIST:
            Locations.append(entity)
            continue


        for loc_tag in LOCATION_TAGS:
            
            if loc_tag.lower() in entity.lower():
                Locations.append(entity)
                break

    '''To Print entites'''
    # for location in Locations:
    #     print(location)

    '''
        Names Extraction from Entities.....
    '''
    for name in set(Entities):
        if name not in Locations:
            names.append(name)

    # for name in names:
    #     print(name)

    # print("\nCrime Word: \n")
    # for crime_word in set(crime_word_list):
    #     print(crime_word)


    '''
        Crime Location Segregation.
    '''
    Locations_copy = deepcopy(Locations)
    Crime_Locations = []
    Non_Crime_Locations = []

    sentences = nltk.sent_tokenize(Text)
    length = len(sentences)
    for i in range(length):
        curr = sentences[i].lower()
        if i == 0:
            prev = None
            Next = sentences[i+1].lower()
        elif i == length-1:
            prev = sentences[i-1].lower()
            Next = None
        else:
            prev = sentences[i-1].lower()
            Next = sentences[i+1].lower()

        flag = False
        for location in Locations_copy:
            if location in curr:
                for crime_word in crime_word_list:
                    if prev and Next:
                        if crime_word in curr or crime_word in prev or crime_word in Next:
                            Crime_Locations.append(location)

                    elif prev:
                        if crime_word in curr or crime_word in prev:
                            Crime_Locations.append(location)

                    elif Next:
                        if crime_word in curr or crime_word in Next:
                            Crime_Locations.append(location)

                    else:
                        if crime_word in curr:
                            Crime_Locations.append(location)

        
        # Crime_Locations = list(set(Crime_Locations))
        for crime_loc in Crime_Locations:
            # print(crime_loc)
            if crime_loc in Locations_copy:
                Locations_copy.remove(crime_loc)


    '''
        Non-Crime Locations Segregation.....
    '''
    for location in Locations:
        if location not in Crime_Locations:
            Non_Crime_Locations.append(location)

    # print("\nNon-Crime Locations: \n")
    # for location in set(Non_Crime_Locations):
    #     print(location)

    # print("\nCrime Locations: \n")
    # for crime_loc in set(Crime_Locations):
    #     print(crime_loc)
    # crime_word_list = crime_type(Text)

    return list(set(names)), list(set(Non_Crime_Locations)), list(set(Crime_Locations)), list(set(crime_word_list))


'''
    NewsArticle Class to store Each Article details.....
'''
class NewsArticle():
    """docstring for NewsArticle"""
    def __init__(self, Names, Non_Crime_Locations, Crime_Locations, Crime_list, text):
        
        self.Names = Names
        self.Non_Crime_Locations = Non_Crime_Locations
        self.Crime_Locations = Crime_Locations
        self.Crime_list = Crime_list
        self.text = text


    def return_entities(self):

        return self.Names, self.Non_Crime_Locations, self.Crime_Locations, self.Crime_list


    def print(self):
        
        print("\nName: ")
        for name in set(self.Names):
            print(name)

        print("\nNon-Crime Locations: ")
        for ncl in set(self.Non_Crime_Locations):
            print(ncl)

        print("\nCrime Locations: ")
        for cl in set(self.Crime_Locations):
            print(cl)

        print("\nCrime Word List: ")
        for cwl in set(self.Crime_list):
            print(cwl)

        print("\nArticle Text: ")
        print(self.text)          
        


    def return_text(self):

        return self.text


    def return_names(self):

        return self.Names

if __name__ == "__main__":

    Names, NCL, CL, CWL = return_entities(sys.argv[1])

    # for name in set(Names):
    #     print(name, end="\n")
    # print(";", end="\n")
    newNames = []
    for name in Names:
        if not any([name in n  and name != n for n in Names]):
            newNames.append(name)

    for name in set(newNames):
        print(name, end="|")
    print(";", end="")
    for ncl in set(NCL+CL):
        print(ncl, end="|")
    print(";", end="")
    # for cl in set(CL):
    #     print(cl, end="|")
    # print(";", end="")
    for cwl in set(CWL):
        print(PORTER.stem(cwl), end="|")
