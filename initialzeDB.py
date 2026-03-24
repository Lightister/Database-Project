"""Authors: Bryan Erickson and Aidan Adams"""
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

def makeTables():
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Household(
        HouseHoldNum TINYINT UNSIGNED AUTO_INCREMENT,
        PRIMARY KEY (HouseHoldNum),
        FirstName VARCHAR(30),
        LastName VARCHAR(30),
        Email VARCHAR(30),
        Balance Decimal(10, 2),
        PhoneNumber VARCHAR(12) 
    )
""")

    #create Watercraft table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Watercraft(
        WaterCraftId VARCHAR(8),
        PRIMARY KEY (WaterCraftId),
        Price Decimal(10, 2),
        WatercraftType VARCHAR(40)
        )
""")

    #create Picnic Shelter table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS PicnicShelters(
        ShelterID TINYINT AUTO_INCREMENT,
        PRIMARY KEY  (ShelterID),
        ShelterName VARCHAR(30),
        Price DECIMAL(10, 2)
        )
""")

    #create Reservations table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Reservations(
        HouseHoldNum TINYINT UNSIGNED,
        WaterCraftId VARCHAR(8),
        ShelterID TINYINT,
        StartTime DATETIME,
        EndTime DATETIME,
        Cost DECIMAL(10,2),
        FOREIGN KEY (HouseHoldNum) REFERENCES Household(HouseHoldNum) ON DELETE CASCADE,
        FOREIGN KEY (WaterCraftId) REFERENCES Watercraft(WaterCraftId),
        FOREIGN KEY (ShelterID) REFERENCES PicnicShelters(ShelterID)
        )
""")
    
    
    #Create Concessions table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Concessions (
        ItemID TINYINT UNSIGNED AUTO_INCREMENT,
        ItemName VARCHAR(20),
        Price DECIMAL(4,2),
        StockAvailable INTEGER UNSIGNED,
        PRIMARY KEY (ItemID)
        )
""")
    
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
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS CampsiteBooking(
    HouseholdNum TINYINT UNSIGNED,
    CampsiteID TINYINT UNSIGNED,
    Cost DECIMAL(10,2),
    NumOfNightsBooked TINYINT UNSIGNED CHECK (NumOfNightsBooked <= 14),
    StartDate DATE NOT NULL,
    EndDate Date NOT NULL,
    PRIMARY KEY (HouseHoldNum, CampsiteID, StartDate),
    FOREIGN KEY (HouseHoldNum) REFERENCES Household(HouseHoldNum) ON DELETE CASCADE,
    FOREIGN KEY (CampsiteID) REFERENCES Campsite(CampsiteID) ON DELETE CASCADE
    )

""")
    
    #Create ConcessionRecipt table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS ConcessionRecipt(
    HouseholdNum TINYINT UNSIGNED,
    ItemID TINYINT UNSIGNED,
    Quantity INTEGER UNSIGNED,
    Cost DECIMAL(4,2),
    PRIMARY KEY (HouseHoldNum, ItemID),   
    FOREIGN KEY (HouseHoldNum) REFERENCES Household(HouseHoldNum) ON DELETE CASCADE,                 
    FOREIGN KEY (ItemID) REFERENCES Concessions(ItemID) ON DELETE CASCADE                 
    )
""")


    

    


def delete():
    myCursor.execute("DROP TABLE IF EXISTS CampsiteBooking")
    myCursor.execute("DROP TABLE IF EXISTS ConcessionRecipt")
    myCursor.execute("DROP TABLE IF EXISTS Reservations")
    myCursor.execute("DROP TABLE IF EXISTS Campsite")
    myCursor.execute("DROP TABLE IF EXISTS PicnicShelters")
    myCursor.execute("DROP TABLE IF EXISTS Watercraft")
    myCursor.execute("DROP TABLE IF EXISTS Concessions")
    myCursor.execute("DROP TABLE IF EXISTS Household")
    

def main():
    #Connect to the database
    initialize_database()
    
    delete()
    #Creates the needed tables
    makeTables()

    
    




if __name__ == "__main__":
    main()
