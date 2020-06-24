import pymysql
import datetime
    
# function to check the presence of a url in tabel
def IsUrlExists(url):
    '''
        TO check if URL exists in DB
        input: url - url of website
    '''
    # print("Article: ", url)
    connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
    if all(ord(char) < 128 for char in url):
        sql = 'SELECT NewsArticleUrl from NewsArticles WHERE NewsArticleUrl Like %s'
        db = connection.cursor()
        db.execute(sql, ('%' + url + '%',))
        result = db.fetchall()
        db.close()
        connection.close()
        if result:
            return True
        else:
            return False
    else:
        return True 
        

# function to convert string date to datetime format
def return_date(date):
    '''
       To convert date into DB input format
    '''
    connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')
    tokens = date.split('T')
    tokens2 = tokens[1].split("+")
    date = tokens[0] + " " + tokens2[0]
    sql = "SELECT DATE_FORMAT(%s, '%%y-%%m-%%d %%h:%%i:%%s') as DATETIME;"
    db = connection.cursor()
    db.execute(sql, (date,))
    
    result = db.fetchall()
    db.close()
    connection.close()
    for res in result:    
        print(res)
        print(res[0])  
        return res[0]
        

# function to enter data into database.
def InsertIntoDatabase(date, url, title, text, location):
    
    new_date = date
    if date:
        new_date = return_date(date)
    else:
        new_date = datetime.datetime.now()
    
    connection = pymysql.connect('localhost', 'root', 'root', 'CRIME_ANALYSIS')

    sql = "INSERT INTO NewsArticles(NewsArticleTitle, NewsArticleText, NewsArticleDate, NewsArticleUrl, Location) values(%s, %s, %s, %s, %s)"

    try:
        db = connection.cursor()
        print("date: ", new_date)
        if db.execute(sql, (title, text, new_date, url, location,)):
            rowId = connection.insert_id()
            print("Row id: ", rowId)
        
        connection.commit()
        db.close()
        connection.close()
    except Exception as e:

        # print(new_date)
        print(e)
        connection.rollback()
        connection.close()
