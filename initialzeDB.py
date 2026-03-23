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
    myCursor.execute("DROP TABLE IF EXISTS Reservations")
    myCursor.execute("DROP TABLE IF EXISTS Campsite")
    myCursor.execute("DROP TABLE IF EXISTS PicnicShelters")
    myCursor.execute("DROP TABLE IF EXISTS Watercraft")
    myCursor.execute("DROP TABLE IF EXISTS Concessions")
    myCursor.execute("DROP TABLE IF EXISTS Household")

    # table for households
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

    fillWatercraft = "INSERT INTO Watercraft VALUES (%s, %s, %s)"
    watercraft = [
        ('PB003', 20.00, 'Paddleboat'),
        ('PB004', 20.00, 'Paddleboat'),
        ('KC005', 35.00, 'Kayak - Tandem'),
        ('SB001', 18.00, 'Stand-Up Board'),
        ('KC006', 35.00, 'Kayak - Tandem'),
        ('KC007', 35.00, 'Kayak - Tandem'),
        ('KC008', 35.00, 'Kayak - Tandem'),
        ('KC009', 35.00, 'Kayak - Tandem'),
        ('KC010', 25.00, 'Kayak - Single'),
        ('CN003', 40.00, 'Canoe'),
        ('RB001', 30.00, 'Rowboat'),
        ('PB005', 20.00, 'Paddleboat'),
        ('SB002', 18.00, 'Stand-Up Board'),
        ('RB002', 30.00, 'Rowboat'),
        ('RB003', 30.00, 'Rowboat'),
        ('SB003', 18.00, 'Stand-Up Board'),
        ('KC011', 25.00, 'Kayak - Single'),
        ('SB004', 18.00, 'Stand-Up Board'),
        ('PB006', 20.00, 'Paddleboat'),
        ('KC012', 35.00, 'Kayak - Tandem'),
        ('PB007', 20.00, 'Paddleboat'),
        ('RB004', 30.00, 'Rowboat'),
        ('SB005', 18.00, 'Stand-Up Board'),
        ('SB006', 18.00, 'Stand-Up Board'),
        ('KC013', 35.00, 'Kayak - Tandem'),
        ('CN004', 40.00, 'Canoe'),
        ('PB008', 20.00, 'Paddleboat'),
        ('RB005', 30.00, 'Rowboat'),
        ('KC014', 35.00, 'Kayak - Tandem'),
        ('KC015', 35.00, 'Kayak - Tandem'),
        ('PB009', 20.00, 'Paddleboat'),
        ('RB006', 30.00, 'Rowboat'),
        ('KC016', 35.00, 'Kayak - Tandem'),
        ('SB007', 18.00, 'Stand-Up Board'),
        ('CN005', 40.00, 'Canoe'),
        ('KC017', 25.00, 'Kayak - Single'),
        ('RB007', 30.00, 'Rowboat'),
        ('SB008', 18.00, 'Stand-Up Board'),
        ('RB008', 30.00, 'Rowboat'),
        ('KC018', 25.00, 'Kayak - Single'),
        ('PB010', 20.00, 'Paddleboat'),
        ('CN006', 40.00, 'Canoe'),
        ('PB011', 20.00, 'Paddleboat'),
        ('KC019', 25.00, 'Kayak - Single'),
        ('CN007', 40.00, 'Canoe'),
        ('SB009', 18.00, 'Stand-Up Board'),
        ('KC020', 25.00, 'Kayak - Single'),
        ('PB012', 20.00, 'Paddleboat'),
        ('KC021', 35.00, 'Kayak - Tandem'),
        ('CN008', 40.00, 'Canoe')
    ]

    myCursor.executemany(fillWatercraft, watercraft)

    fillShelters = "INSERT INTO PicnicShelters VALUES (%s, %s, %s)"
    shelters = [
        (6,  'Magnolia Shelter', 60.00),
        (7,  'Cedar Shelter',    55.00),
        (8,  'Redwood Shelter',  45.00),
        (9,  'Hickory Shelter',  55.00),
        (10, 'Birch Shelter',    50.00),
        (11, 'Maple Shelter',    45.00),
        (12, 'Magnolia Shelter', 65.00),
        (13, 'Maple Shelter',    65.00),
        (14, 'Poplar Shelter',   55.00),
        (15, 'Hickory Shelter',  45.00),
        (16, 'Redwood Shelter',  65.00),
        (17, 'Maple Shelter',    40.00),
        (18, 'Cedar Shelter',    40.00),
        (19, 'Maple Shelter',    55.00),
        (20, 'Walnut Shelter',   70.00),
        (21, 'Spruce Shelter',   40.00),
        (22, 'Magnolia Shelter', 55.00),
        (23, 'Walnut Shelter',   40.00),
        (24, 'Maple Shelter',    50.00),
        (25, 'Hickory Shelter',  40.00),
        (26, 'Spruce Shelter',   50.00),
        (27, 'Maple Shelter',    60.00),
        (28, 'Spruce Shelter',   45.00),
        (29, 'Magnolia Shelter', 70.00),
        (30, 'Birch Shelter',    65.00),
        (31, 'Willow Shelter',   55.00),
        (32, 'Elm Shelter',      60.00),
        (33, 'Spruce Shelter',   70.00),
        (34, 'Poplar Shelter',   45.00),
        (35, 'Aspen Shelter',    65.00),
        (36, 'Fir Shelter',      40.00),
        (37, 'Maple Shelter',    65.00),
        (38, 'Sycamore Shelter', 65.00),
        (39, 'Hickory Shelter',  70.00),
        (40, 'Chestnut Shelter', 45.00),
        (41, 'Hickory Shelter',  55.00),
        (42, 'Cedar Shelter',    40.00),
        (43, 'Cedar Shelter',    45.00),
        (44, 'Elm Shelter',      45.00),
        (45, 'Maple Shelter',    55.00),
        (46, 'Maple Shelter',    45.00),
        (47, 'Magnolia Shelter', 60.00),
        (48, 'Aspen Shelter',    70.00),
        (49, 'Fir Shelter',      70.00),
        (50, 'Willow Shelter',   70.00),
        (51, 'Elm Shelter',      40.00),
        (52, 'Sycamore Shelter', 70.00),
        (53, 'Aspen Shelter',    45.00),
        (54, 'Walnut Shelter',   40.00),
        (55, 'Redwood Shelter',  50.00)
    ]

    myCursor.executemany(fillShelters, shelters)

    fillHouseholds = "INSERT INTO Household VALUES (%s, %s, %s, %s. %s, %s)"

    households = [
        (201, 'Emma',      'Nguyen',    'emma.nguyen@icloud.com',          199.55, '608-495-7784'),
        (202, 'Daniel',    'Wright',    'daniel.wright@outlook.com',        360.83, '608-889-8274'),
        (203, 'Amelia',    'Martin',    'ameliamartin29@gmail.com',         437.12, '938-421-4581'),
        (204, 'Zoey',      'Rivera',    'zoeyrivera@icloud.com',            148.19, '969-182-8173'),
        (205, 'Sofia',     'Taylor',    'sofia.taylor65@proton.me',         437.30, '688-646-3085'),
        (206, 'Harper',    'Ramirez',   'harper_ramirez@outlook.com',       189.48, '894-718-8209'),
        (207, 'Charlotte', 'Harris',    'charlotte_harris26@gmail.com',     333.53, '911-402-4166'),
        (208, 'Luke',      'Nelson',    'luke.nelson82@proton.me',          208.36, '970-987-4788'),
        (209, 'Sofia',     'Thompson',  'sofiathompson@gmail.com',          250.83, '407-101-9554'),
        (210, 'Mason',     'Baker',     'masonbaker22@yahoo.com',           131.95, '956-526-8668'),
        (211, 'Aiden',     'King',      'aidenking80@yahoo.com',            369.62, '307-925-6038'),
        (212, 'Ava',       'Nguyen',    'ava.nguyen8@outlook.com',          184.61, '770-741-5836'),
        (213, 'Charlotte', 'Carter',    'charlotte.carter51@yahoo.com',     132.40, '536-231-3140'),
        (214, 'Avery',     'Hall',      'averyhall50@hotmail.com',          477.17, '383-468-5098'),
        (215, 'Lucas',     'Moore',     'lucas_moore74@yahoo.com',          413.33, '690-686-8804'),
        (216, 'Luke',      'Hernandez', 'luke.hernandez@icloud.com',        261.59, '317-437-9095'),
        (217, 'Ava',       'Perez',     'avaperez@hotmail.com',             340.31, '481-748-1196'),
        (218, 'Owen',      'Lee',       'owen_lee@yahoo.com',               294.07, '248-506-1592'),
        (219, 'Noah',      'Perez',     'noahperez30@yahoo.com',            418.92, '258-812-7843'),
        (220, 'Amelia',    'Gonzalez',  'amelia.gonzalez@outlook.com',      137.75, '573-172-4247'),
        (221, 'Aurora',    'Scott',     'aurora.scott90@proton.me',         479.98, '747-183-2860'),
        (222, 'Riley',     'Rodriguez', 'riley.rodriguez@gmail.com',        379.59, '862-488-3728'),
        (223, 'Emily',     'Rivera',    'emily.rivera@outlook.com',         386.59, '550-928-8145'),
        (224, 'Charlotte', 'Martin',    'charlotte.martin@yahoo.com',       248.28, '733-848-1205'),
        (225, 'Amelia',    'Harris',    'ameliaharris@hotmail.com',         221.92, '816-995-2313'),
        (226, 'Mia',       'Hernandez', 'mia_hernandez48@outlook.com',      294.65, '798-506-1333'),
        (227, 'Mason',     'Hernandez', 'mason.hernandez2@hotmail.com',     147.87, '326-604-8004'),
        (228, 'Ava',       'Williams',  'ava_williams21@outlook.com',       332.00, '235-485-5434'),
        (229, 'Samuel',    'Anderson',  'samuelanderson@outlook.com',       369.47, '629-624-4732'),
        (230, 'Benjamin',  'King',      'benjamin_king@yahoo.com',          323.90, '367-963-2539'),
        (231, 'Logan',     'Smith',     'logansmith@yahoo.com',             450.29, '384-744-5922'),
        (232, 'Noah',      'Taylor',    'noah.taylor75@yahoo.com',            1.61, '859-136-9240'),
        (233, 'Michael',   'Lewis',     'michael.lewis@outlook.com',        217.33, '689-726-2490'),
        (234, 'Daniel',    'Allen',     'daniel.allen30@yahoo.com',         357.73, '302-546-4304'),
        (235, 'Benjamin',  'Rodriguez', 'benjamin_rodriguez@yahoo.com',     420.45, '462-271-9451'),
        (236, 'David',     'Allen',     'davidallen@yahoo.com',             262.25, '903-821-7897'),
        (237, 'Michael',   'King',      'michaelking@outlook.com',          162.02, '778-442-9121'),
        (238, 'Charlotte', 'Miller',    'charlottemiller@icloud.com',        31.08, '394-151-5798'),
        (239, 'Benjamin',  'Moore',     'benjaminmoore@hotmail.com',        265.16, '400-843-6972'),
        (240, 'James',     'Hernandez', 'james_hernandez@proton.me',        152.53, '466-302-8412'),
        (241, 'Noah',      'Johnson',   'noah_johnson@hotmail.com',          39.16, '588-118-6879'),
        (242, 'Abigail',   'Harris',    'abigail.harris@gmail.com',          10.77, '380-316-4639'),
        (243, 'Ethan',     'Flores',    'ethan_flores@proton.me',             0.37, '316-773-8140'),
        (244, 'Elijah',    'Hall',      'elijahhall48@icloud.com',          279.17, '584-886-5306'),
        (245, 'Abigail',   'Rivera',    'abigail_rivera15@hotmail.com',     121.74, '234-324-5375'),
        (246, 'Abigail',   'Flores',    'abigail.flores35@hotmail.com',     312.43, '417-552-8286'),
        (247, 'Jack',      'Johnson',   'jackjohnson96@gmail.com',          388.36, '324-855-1290'),
        (248, 'Evelyn',    'Young',     'evelynyoung57@outlook.com',        254.83, '440-719-9758'),
        (249, 'Sophia',    'Jackson',   'sophia_jackson@hotmail.com',       462.64, '664-860-9029'),
        (250, 'Ethan',     'Hill',      'ethan.hill@gmail.com',             281.55, '849-232-7717')
    ]
    myCursor.executemany(fillHouseholds, households)

    
    #Adds data to the concessions table
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
        ('Chips', 1.25 , 58),
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
