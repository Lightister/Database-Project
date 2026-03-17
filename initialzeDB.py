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

def createTables():
    #Remove all tables
    myCursor.execute("DROP TABLE IF EXISTS CampsiteBooking")
    myCursor.execute("DROP TABLE IF EXISTS ConcessionRecipt")
    myCursor.execute("DROP TABLE IF EXISTS Campsite")
    myCursor.execute("DROP TABLE IF EXISTS Concessions")
    myCursor.execute("DROP TABLE IF EXISTS Household")

    #Dummy table for households
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS Household(
    HouseHoldNum TINYINT UNSIGNED AUTO_INCREMENT,
    PRIMARY KEY (HouseHoldNum)
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
    
def initializeTables():
    #Resets and repopulates the campsite table
    fillCampsites = "INSERT INTO Campsite (Sitename, Price) VALUES (%s, %s)"
    campsites =[
        ('A01', 15.75),
        ('A02', 15.75),
        ('A03', 15.75),
        ('A04', 15.75),
        ('A05', 15.75),
        ('A06', 15.75),
        ('A07', 15.75),
        ('A08', 15.75),
        ('A09', 15.75),
        ('A10', 15.75),
        ('B01', 10.29),
        ('B02', 10.29),
        ('B03', 10.29),
        ('B04', 10.29),
        ('B05', 10.29),
        ('B06', 10.29),
        ('B07', 10.29),
        ('B08', 10.29),
        ('B09', 10.29),
        ('B10', 10.29),
        ('C01', 38.83),
        ('C02', 38.83),
        ('C03', 38.83),
        ('C04', 38.83),
        ('C05', 38.83),
        ('C06', 38.83),
        ('C07', 38.83),
        ('C08', 38.83),
        ('C09', 38.83),
        ('C10', 38.83),
    ]
    myCursor.executemany(fillCampsites, campsites)
    
    
    fillConcessions = "INSERT INTO Concessions (ItemName, Price, StockAvailable) VALUES (%s, %s, %s)"
    concessions = [
        ('Tent', 85.00 , 3),
        ('Stakes', 15.30, 18 ),
        ('Tarp', 25.00 , 4 ),
        ('Detergent', 8.98 , 10),
        ('Battery', 12.64, 19),
        ('Flashlight', 5.06, 28),
        ('Sunscreen',7.94 , 13),
        ('Bug Spray', 6.49 ,11 ),
        ('Matches',0.25 , 50),
        ('Lighter',3.56 , 25),
        ('Firestarter',2.75 , 28),
        ('Lantern', 5.82, 11),
        ('Propane', 10.38, 6),
        ('Chips',1.25 , 58),
        ('Chcolate', 1.25, 37),
        ('Marshmallows', 4.35, 21),
        ('Graham Crackers ', 8.43 , 14),
        ('Ice Cream', 3.50 , 59 ),
        ('Hot Dog', 6.50, 16),
        ('Hamburger', 6.50, 13),
    ]
    myCursor.executemany(fillConcessions,concessions)


    

def main():
    #Initliaze the the database
    initialize_database()
    
    #Creates the needed tables
    createTables()

    #Initializes the tables with starting data
    initializeTables()




if __name__ == "__main__":
    main()