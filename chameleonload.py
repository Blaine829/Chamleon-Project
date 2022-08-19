import csv
import json
import mysql.connector


file = open("Chameleon.csv", "r")
WordCat = {}

db = mysql.connector.connect(user='friday', password='mypassword', host='localhost', database='Chameleon')
cursor = db.cursor()

cursor.execute('Select * from Category')
x = cursor.fetchall()
print(len(x))
for line in file.readlines():
    l = line.split(',')
    if l[0] in WordCat:
        WordCat[l[0]].append(l[1][0:-1])
    else:
        WordCat[l[0]] = [l[1][0:-1]] 
del WordCat['Category']
print(WordCat)

for items in WordCat:
    #get categoryID
    print(items)
    categoryIDQuery = " ".join(['SELECT CategoryID',
                        'FROM Category',
                        'WHERE Category=' + '"' + items  + '";'])
    cursor.execute(categoryIDQuery)
    resultset = cursor.fetchall()
    CategoryID = resultset[0][0]
    print(str(CategoryID) + ", " + items)
    
    for words in WordCat[items]:
        #get word ID
        wordIDQuery = " ".join(['SELECT WordID',
                        'FROM Words',
                        'WHERE Word=' + '"' + words  + '";'])
        cursor.execute(wordIDQuery)
        resultset = cursor.fetchall()
        WordID = resultset[0][0]
        print(str(WordID) + ", " + words)
        #insert CatID, WordID into WordCategory
        
        insertion = 'INSERT INTO WordCategory (CategoryID, WordID) VALUES (%s, %s)'
        cursor.execute(insertion, (CategoryID, WordID))
    
    
db.commit()               
db.close()