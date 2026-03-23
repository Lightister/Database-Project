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
    EXPLAIN SELECT * FROM Campsite
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

def showShelters
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

def mainMenu():
    #Main menu
    endMenu = False

    while(not endMenu):
        print("Select an option:")
        print("1: Show all campsites")
        print("2: Show all concessions")
        print("3: Show all watercraft")
        print("4: Show all picnic shelters")
        print("3: Add new household")
        print("4: Campsite reservation options")
        print("5: Watercraft reservation options")
        print("6: Picnic shelter reservation options")

        menuOption = int(input("Option: "))

        if menuOption == 1:
            showCampsites()
        elif menuOption == 2:
            showConcessions()
        elif menuOption == 3:
            showWatercraft()
        elif menuOption == 4:
            print("option selected")
        elif menuOption == 5:
            print("option selected")
        elif menuOption == 6:
            print("option selected")
        else:
            endMenu = True 





    

def main():
    #Connect to the database
    initialize_database()

    #Display the main menu
    mainMenu()
    
    

    



if __name__ == "__main__":
    main()
