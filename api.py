import flask
import mysql.connector
import json
import random
from flask import render_template


db = mysql.connector.connect(user='friday', password='mypassword', host='localhost', database='Chameleon')
cursor = db.cursor()

app = flask.Flask(__name__)
app.config["DEBUG"] = True

#Home Route
@app.route('/')
def home():
    return render_template("joinGame.html")
    
#Get a random category and it's associated words
@app.route('/randomCategory', methods=['GET'])
def randomCategory():
    """
    cursor = db.cursor()
    members = ' '.join(['SELECT id, alias', 'FROM Members'])
    cursor.execute(members)
    membersResult = cursor.fetchall()
    return json.dumps(membersResult, sort_keys=True, indent=4)
    """
    #Fetch a random category

    cursor.execute('Select Category from Category ORDER BY RAND() LIMIT 1;')
    Category = cursor.fetchall()
    
    #Get the words for that category

    cursor.execute('SELECT Word FROM Category NATURAL JOIN WordCategory NATURAL JOIN Words WHERE Category.Category = "' + Category[0][0] + '";')
    Words = cursor.fetchall()
    
    
    wordList = []
    for word in Words:
        wordList.append(word[0])
    print(wordList)
    
    #Formulate a Category/Word Dictionary
    wordCategoryDictionary = {}
    wordCategoryDictionary[Category[0][0]] = wordList
    print(wordCategoryDictionary)
    return json.dumps(wordCategoryDictionary, indent = 4) 

#Creates a game instance
@app.route('/createGame', methods=['GET'])
def createGame():
    

     #Fetch a random category
    cursor.execute('Select CategoryID from Category ORDER BY RAND() LIMIT 1;')
    CategoryID = cursor.fetchall()[0][0]
    
    #Get the words for that category
    cursor.execute('SELECT WordID FROM Category NATURAL JOIN WordCategory NATURAL JOIN Words WHERE Category.CategoryID = "' + str(CategoryID) + '";')
    
    #Choose a random word
    randomNumber = random.randint(0,15)
    WordID = cursor.fetchall()[randomNumber][0]

    #Insert values into Game Table
    insertion = 'INSERT INTO Game (CategoryID, ChosenWord, Status) VALUES (%s,%s, %s)'
    cursor.execute(insertion, (CategoryID, WordID, "Waiting"))
    db.commit() 
    
    #Save the game ID
    GameID = str(cursor.lastrowid)
    
    #Insert new addition to player's table. 
    insertion = 'INSERT INTO Players (GameID) VALUES (%s)'
    cursor.execute(insertion, ([cursor.lastrowid]))
    db.commit() 
    PlayerID = str(cursor.lastrowid)
    return '{} {}'.format(GameID, PlayerID)


    
#Add a player to the players table and return the ID
@app.route('/addPlayer/<GameID>', methods=['GET'])
def addPlayer(GameID):
    insertion = 'INSERT INTO Players (GameID) VALUES (%s)'
    cursor.execute(insertion, ([GameID]))
    db.commit() 
    PlayerID = str(cursor.lastrowid)
    return PlayerID

#Return a list of open games
@app.route('/openGames', methods=['GET'])
def openGames():
    cursor.execute('Select GameID from Game WHERE Status="Waiting"')
    openGames = cursor.fetchall()
    Games = []
    for game in openGames:
        Games.append(game[0])
 
    return json.dumps(Games)
    
#Check if game has started
@app.route('/checkGameStatus/<GameID>', methods=['GET'])
def checkGameStatus(GameID):
    cursor.execute('SELECT STATUS FROM Game WHERE GameID=' + GameID)
    status = cursor.fetchall()
    
    return status[0][0]

#Return the game's words, player status, and chosen word
@app.route('/populateGame/<GameID>/<PlayerID>', methods=['GET'])
def getWords(GameID, PlayerID):
    cursor.execute('SELECT CategoryID FROM Game WHERE GameID=' + GameID)
    CategoryID = cursor.fetchall()
    
    cursor.execute('SELECT Word FROM Category NATURAL JOIN WordCategory NATURAL JOIN Words WHERE Category.CategoryID =' + str(CategoryID[0][0]))
    Words = cursor.fetchall()
    
    cursor.execute('SELECT Category FROM Category WHERE CategoryID='+ str(CategoryID[0][0]))
    Category = cursor.fetchall()
    
    wordList = []
    for word in Words:
        wordList.append(word[0])
    print(wordList)
    
    #Formulate a Category/Word Dictionary
    wordCategoryDictionary = {}
    wordCategoryDictionary["Words"] = wordList
    wordCategoryDictionary["Category"] = Category[0][0]
    print(wordCategoryDictionary)
    
    #Get the chosen word
    cursor.execute('SELECT ChosenWord FROM Game WHERE GameID =' + GameID)
    ChosenWordID = cursor.fetchall()[0][0]
    cursor.execute('SELECT Word FROM Words WHERE WordID =' + str(ChosenWordID))
    ChosenWord = str(cursor.fetchall()[0][0])
    
    #Get player status as Chameleon
    cursor.execute('SELECT IsChameleon FROM Players WHERE PlayerID=' + str(PlayerID))
    PlayerStatus = str(cursor.fetchall()[0][0])
        
    wordCategoryDictionary["Keyword"] = ChosenWord
    wordCategoryDictionary["Player Status"] = PlayerStatus

    return json.dumps(wordCategoryDictionary)
    
    
@app.route('/startGame/<GameID>', methods=['GET'])
def startGame(GameID):
    #Choose a player to be the Chameleon
    cursor.execute('Select PlayerID FROM Players WHERE GameID=' + str(GameID) + ' ORDER BY RAND() LIMIT 1;')
    RandPlayerID = cursor.fetchall()[0][0]
    cursor.execute('update Players SET IsChameleon = true WHERE PlayerID =' + str(RandPlayerID))
    db.commit() 
    
    
    #Set status to started 
    cursor.execute('update Game SET Status = "Started" WHERE GameID = ' + str(GameID))
    db.commit() 
    
    
    return str(RandPlayerID)
    
    
@app.route('/endGame/<GameID>', methods=['GET'])
def endGame(GameID):
    #Set the game status to finished
    cursor.execute('update Game SET Status = "Finished" WHERE GameID = ' + str(GameID))
    db.commit()
    return "Game finished"

    
def main():
    print('hello')
    app.run(host='0.0.0.0', port=8080)

if __name__ == "__main__":
    main()
        


              
db.close()