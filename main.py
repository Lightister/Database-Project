"""Authors: Bryan Erickson and Aidan Adams"""
import mysql.connector

def initialize_database():
    #Connects to the MySQL server
    global db
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="wordPass12"
    ) 

    #Creating a global cursor object
    global myCursor
    myCursor = db.cursor()

    #Creates the database if it doesn't exist and uses it
    myCursor.execute("CREATE DATABASE IF NOT EXISTS Campground")
    myCursor.execute("USE Campground")

def createTables():
    #create campsite table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Campsite(
        CampsiteID TINYINT UNSIGNED AUTO_INCREMENT,
        SiteName CHAR(3) UNIQUE,
        Price DECIMAL(4,2),
        PRIMARY KEY (CampsiteID)
        )
""")

    #Create CampsiteBooking table

    #Create Concessions table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Concessions (
        ItemID TINYINT UNSIGNED AUTO_INCREMENT,
        ItemName VARCHAR(20),
        Price DECIMAL(4,2),
        StockAvailable INTEGER,
        PRIMARY KEY (ItemID)
        )
""")

    #Create ConcessionRecipt table
    

def main():
    #Initliaze the the database
    initialize_database()
    
    #Initialize the needed tables
    createTables()

    myCursor.execute("SHOW TABLES")

    for x in myCursor:
        print(x)



if __name__ == "__main__":
    main()