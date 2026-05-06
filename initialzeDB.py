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
    PRIMARY KEY (HouseholdNum, CampsiteID, StartDate),
    FOREIGN KEY (HouseholdNum) REFERENCES Household(HouseHoldNum) ON DELETE CASCADE,
    FOREIGN KEY (CampsiteID) REFERENCES Campsite(CampsiteID) ON DELETE CASCADE
    )

""")
    
    #Create ConcessionRecipt table
    myCursor.execute("""
    CREATE TABLE IF NOT EXISTS ConcessionRecipt(
    HouseholdNum TINYINT UNSIGNED,
    ItemID TINYINT UNSIGNED,
    Quantity INTEGER UNSIGNED,
    Cost DECIMAL(7,2),
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


def makeProcedure():
    myCursor.execute("""
    DROP PROCEDURE IF EXISTS MakeCampsiteReservation
""")
    myCursor.execute("""

CREATE PROCEDURE MakeCampsiteReservation(
                     IN p_householdNum INT,
                     IN p_campsiteName VARCHAR(100),
                     IN p_startDate DATE,
                     IN p_endDate DATE
                     )
                     BEGIN

                     INSERT INTO CampsiteBooking (HouseholdNum, CampsiteID, Cost, NumOfNightsBooked, StartDate, EndDate)
                         SELECT p_householdNum, c.CampsiteID, c.Price * DATEDIFF(p_endDate, p_startDate), DATEDIFF(p_endDate, p_startDate), p_startDate , p_endDate
                         FROM Campsite AS c
                         
                         WHERE c.SiteName = p_campsiteName

                         AND
                            (DATEDIFF(p_endDate, p_startDate)) <= 14
                         AND
                         (
                         SELECT COALESCE(SUM(DATEDIFF(EndDate, StartDate)), 0)
                         FROM CampsiteBooking
                         WHERE HouseholdNum = p_householdNum
                         AND StartDate >= DATE_SUB(p_startDate, INTERVAL 30 DAY)
                         
                         ) + DATEDIFF(p_endDate, p_startDate) <= 14

                         AND NOT EXISTS
                         (SELECT 1
                         FROM Campsitebooking AS c
                         WHERE c.HouseholdNum =  p_householdNum 
                         AND ((p_startDate BETWEEN c.StartDate AND c.EndDate)
                         OR (p_endDate BETWEEN c.StartDate AND c.EndDate)) 
                         )

                         AND NOT EXISTS
                         (
                         SELECT 1 
                         FROM Campsitebooking AS c
                         WHERE c.SiteName = p_campsiteName 
                         AND ((p_startDate BETWEEN c.StartDate AND c.EndDate)
                         OR (p_endDate BETWEEN c.StartDate AND c.EndDate))
                         );
                        END

""")

def main():
    #Connect to the database
    initialize_database()
     
    delete()
    #Creates the needed tables
    makeTables()

    makeProcedure()
    
    




if __name__ == "__main__":
    main()