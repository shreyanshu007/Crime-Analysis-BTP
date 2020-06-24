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
