import pymysql

list1 = [14399,34409,43171,63187,63655,63681,64122,64211,64734,64398,65948,65997,66077,66308,66916,68137,67595,68392,68390,68393]
list2 = [3,4,12,35,40,49,67,68,74,81,95,117,119,133,139,147,148,169,172,178]

def fetch_from_db(articleID=None):
	connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
	sql = "SELECT * FROM NewsArticles WHERE NewsArticleID = %s"
	text = None
	try:
		with connection:
			db = connection.cursor()
			result = db.execute(sql,(articleID))
			result = db.fetchall()
			text = result[0]
			connection.commit()

	except Exception as e:
		connection.rollback()
	finally:
		db.close()
		connection.close()

	#print(articleID, text)
	return text


def similar_data():
	data = []
	for item in list1:
		data.append(fetch_from_db(item))
	return data

def different_data():
	data = []
	for item in list2:
		data.append(fetch_from_db(item))
	return data

if __name__ == '__main__':
	print(similar_data())
	print(different_data())
