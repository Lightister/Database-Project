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


def showCampsites():
    myCursor.execute("""
    SELECT * FROM Campsite
""")
    
    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)
def showHouseholds():
    myCursor.execute("""
    SELECT * FROM Household
    """)

    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)
def showWaterReservations():
    myCursor.execute("""
    SELECT WaterCraftId, HouseholdNum FROM Reservations, Watercraft WHERE HouseholdNum = HouseholdNum
    """)

def showWatercraft():
    myCursor.execute("SELECT * FROM Watercraft")
    myResult = myCursor.fetchall()

    for x in myResult:
        print (x)

def showShelters():
    myCursor.execute("""
    SELECT * FROM PicnicShelters
    """)

    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)
def showConcessions():
    myCursor.execute("SELECT * FROM Concessions")
    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)
        
        
def campsiteReservationOption():
    def viewAllReservations():
        myCursor.execute("SELECT * FROM CampsiteBooking")
        myResult = myCursor.fetchall()

        for x in myResult:
            print(x)
        
    def makeNewReservation():
        householdNum = int(input("Enter household number:"))
        campsiteName = (input("Enter campsite to book:"))
        startDate = input("Enter start date:")
        endDate = input("Enter end date:")

        

        myCursor.execute("""
        INSERT INTO CampsiteBooking (HouseholdNum, CampsiteID, Cost, NumOfNightsBooked, StartDate, EndDate)
                         SELECT %(householdNum)s, c.CampsiteID, c.Price * DATEDIFF(%(endDate)s, %(startDate)s), DATEDIFF(%(endDate)s, %(startDate)s), %(startDate)s , %(endDate)s
                         FROM Campsite AS c
                         
                         WHERE c.SiteName = %(campsiteName)s

                         AND
                            (DATEDIFF(%(endDate)s, %(startDate)s)) <= 14
                         AND
                         (
                         SELECT COALESCE(SUM(DATEDIFF(EndDate, StartDate)), 0)
                         FROM CampsiteBooking
                         WHERE HouseholdNum = %(householdNum)s
                         AND StartDate >= DATE_SUB(%(startDate)s, INTERVAL 30 DAY)
                         
                         ) + DATEDIFF(%(endDate)s, %(startDate)s) <= 14

                         AND NOT EXISTS
                         (SELECT 1
                         FROM Campsitebooking AS c
                         WHERE c.HouseholdNum =  %(householdNum)s 
                         AND ((%(startDate)s BETWEEN c.StartDate AND c.EndDate)
                         OR (%(endDate)s BETWEEN c.StartDate AND c.EndDate)) 
                         )

                         AND NOT EXISTS
                         (
                         SELECT 1 
                         FROM Campsitebooking AS c
                         WHERE c.SiteName = %(campsiteName)s 
                         AND ((%(startDate)s BETWEEN c.StartDate AND c.EndDate)
                         OR (%(endDate)s BETWEEN c.StartDate AND c.EndDate))
                         )
                        

                        """,{
                            "householdNum": householdNum,
                            "campsiteName": campsiteName,
                            "startDate": startDate,
                            "endDate": endDate
                        })
        print("Rows inserted:", myCursor.rowcount) 
     
        
        
    def seeHouseholdReservations():
        print("h")
    
    def reservationsForDate():
        print("g")
    
    endSubMenu = False
    while(not endSubMenu):
        print("Select an option:")
        print("1: View all")
        print("2: Make new reservation")
        print("3: See all reservations for a household")
        print("4: See all by date")
        menuOption = int(input("Option: "))
        
        if menuOption == 1:
            viewAllReservations()
        elif menuOption == 2:
            makeNewReservation()
        elif menuOption == 3:
            seeHouseholdReservations()
        elif menuOption == 4:
           reservationsForDate()
        else:
            endSubMenu = True

def mainMenu():
    #Main menu
    endMenu = False

    while(not endMenu):
        print("Select an option:")
        print("1: Show all campsites")
        print("2: Show all concessions")
        print("3: Show all watercraft")
        print("4: Show all picnic shelters")
        print("5: Add new household")
        print("6: Campsite reservation options")
        print("7: Watercraft reservation options")
        print("8: Picnic shelter reservation options")

        menuOption = int(input("Option: "))
        if menuOption == 1:
            showCampsites()
        elif menuOption == 2:
            showConcessions()
        elif menuOption == 3:
            showWatercraft()
        elif menuOption == 4:
            showShelters()
        elif menuOption == 5:
            print("option selected")
        elif menuOption == 6:
            campsiteReservationOption()
        else:
            endMenu = True 





    

def main():
    #Connect to the database
    initialize_database()

    #Display the main menu
    mainMenu()
    
    

    



if __name__ == "__main__":
    main()
