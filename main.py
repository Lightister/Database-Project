"""Authors: Bryan Erickson and Aidan Adams

!!!!!!! Run 'initializeDB.py' before using this program !!!!!!!
"""
import mysql.connector

def initialize_database():
    #Connects to the MySQL server
    global db
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="wordPass12",
        autocommit = True
    ) 

    #Creating a global cursor object
    global myCursor
    myCursor = db.cursor(buffered=True)

    #Creates the database if it doesn't exist and uses it
    myCursor.execute("CREATE DATABASE IF NOT EXISTS Campground")
    myCursor.execute("USE Campground")


    

def main():
    #Connect to the database
    initialize_database()
    
    myCursor.execute("SHOW TABLES")

    for x in myCursor:
        print(x)



if __name__ == "__main__":
    main()