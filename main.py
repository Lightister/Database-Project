"""Authors: Bryan Erickson and Aidan Adams

!!!!!!! Run 'initializeDB.py' and 'Generator.py' before using this program !!!!!!!
"""

import mysql.connector
from tabulate import tabulate


def initialize_database():
    # Connects to the MySQL server
    global db
    db = mysql.connector.connect(
        host="localhost", user="root", password="wordPass12", autocommit=True
    )

    # Creating a global cursor object
    global myCursor
    myCursor = db.cursor(buffered=True)

    # Creates the database if it doesn't exist and uses it
    myCursor.execute("CREATE DATABASE IF NOT EXISTS Campground")
    myCursor.execute("USE Campground")

    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)


def showHouseholds():
    myCursor.execute("""
    SELECT * FROM Household
    """)

    rows = myCursor.fetchall()
    headers = [col[0] for col in myCursor.description]

    print(tabulate(rows, headers=headers, tablefmt="grid"))


##Shows all shelter reservations and the households that are suing them
def showShelterReservations():
    myCursor.execute("""
    SELECT ShelterId, HouseholdNum 
    FROM Reservations, PicnicShelters 
    WHERE HouseholdNum = HouseholdNum
    """)


##Show all reciepts with item costs and names
def purchasedItems():
    myCursor.execute("""
    SELECT ItemId, ItemName, Price
    FROM ConcessionRecipt, Concessions
    WHERE ItemId = ItemId
    """)


##Shows the average price of all watercraft
def WatercraftAvg():
    myCursor.execute("""
    SELECT WaterCraftID, AVG(Price) AS Mean_Price
    FROM Watercraft
    GROUP BY
    WaterCraftID
    """)


##Find all households with zero or negative balance with a booked campsite
def OverDue():
    myCursor.execute("""
    SELECT * FROM CampsiteBooking
    WHERE HouseholdNum IN (
        Select HouseholdNum FROM Household
        WHERE Balance <=0
    )
    """)


## Find all concession receipts with cost less than price(for discounts)
def discountedItems():
    myCursor.execute("""
    SELECT * FROM ConcessionRecipt
    WHERE Cost < (
        SELECT Price FROM Concessions
        WHERE Concessions.ItemID = ConcessionRecipt.ItemID
    )
    """)


## Check if any item out of stock
## see if this runs later σ_{StockAvailable < 1}(Concessions)


def showWaterReservations():
    myCursor.execute("""
    SELECT WaterCraftId, HouseholdNum FROM Reservations, Watercraft WHERE HouseholdNum = HouseholdNum
    """)


def showWatercraft():
    myCursor.execute("SELECT * FROM Watercraft")
    rows = myCursor.fetchall()
    headers = [col[0] for col in myCursor.description]

    print(tabulate(rows, headers=headers, tablefmt="grid"))


def showShelters():
    myCursor.execute("""
    SELECT * FROM PicnicShelters
    """)

    rows = myCursor.fetchall()
    headers = [col[0] for col in myCursor.description]

    print(tabulate(rows, headers=headers, tablefmt="grid"))


def campsiteReservationOption():
    def viewAllReservations():
        myCursor.execute("SELECT * FROM CampsiteBooking")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def makeNewReservation():
        try:
            householdNum = int(input("Enter household number: "))
            campsiteName = input("Enter campsite to book: ")
            startDate = input("Enter start date: ")
            endDate = input("Enter end date: ")

            db.start_transaction()

            # Procedure call to make a campsite reservation
            myCursor.callproc(
                "MakeCampsiteReservation", [householdNum, campsiteName, startDate, endDate]
            )

            # Update the household's balance
            myCursor.execute(
                    """
                UPDATE Household
                INNER JOIN Campsite AS c ON %(campsiteName)s = c.SiteName
                SET Balance = (Balance + c.Price * DATEDIFF(%(endDate)s, %(startDate)s))
                WHERE HouseHoldNum = %(householdNum)s
                

                """,
                    {
                        "householdNum": householdNum,
                        "campsiteName": campsiteName,
                        "startDate": startDate,
                        "endDate": endDate,
                    },
                )
            db.commit()
            print("Booking added succesfully")
        
        #Handles errors with the database, rolls-back transaction
        except mysql.connector.Error as dbError:
            print("Error with the database, transaction rolled-back:", dbError)
            db.rollback()

        #Handles any other error, rolls-back transaction
        except Exception as e:
            print("An error occured, transaction was rolled-back: ", e)
            db.rollback()
            

    def seeHouseholdReservations():
        householdNum = int(input("Enter household number: "))
        myCursor.execute(
            """
        SELECT * FROM CampsiteBooking
        WHERE HouseholdNum = %(householdNum)s
        ORDER BY StartDate ASC;
""",
            {"householdNum": householdNum},
        )
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def reservationsForDate():
        myCursor.execute("""
        SELECT * FROM CampsiteBooking
        ORDER BY StartDate ASC;
""")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def avgStayLength():
        myCursor.execute("""
        SELECT cb.CampsiteID, c.SiteName, AVG(cb.NumOfNightsBooked) AS AvgNightsBooked
        FROM CampsiteBooking AS cb
        INNER JOIN Campsite AS c ON cb.CampsiteID = c.CampsiteID
        GROUP BY cb.CampsiteID, c.SiteName
        ORDER BY AvgNightsBooked ASC;

""")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def deleteReservation():
        householdNum = int(input("Enter household number: "))
        startDate = input("Enter start date: ")

        db.start_transaction()

        # Get the total price for the booking
        myCursor.execute(
            """
        SELECT Cost FROM CampsiteBooking
                         WHERE HouseholdNum = %(householdNum)s
                         AND StartDate = %(startDate)s
""",
            {"householdNum": householdNum, "startDate": startDate},
        )
        totalPrice = float(myCursor.fetchone()[0])

        # Check if a booking was found
        if myCursor.rowcount == 0:
            print("A booking for this household number and/or start-date was not found")
            # End transaction if a booking was not found
            db.rollback()
        else:
            # Delete reservation and update household balance
            myCursor.execute(
                """  
           DELETE FROM CampsiteBooking
                        WHERE HouseholdNum = %(householdNum)s
                         AND StartDate = %(startDate)s
""",
                {"householdNum": householdNum, "startDate": startDate},
            )

            myCursor.execute(
                """
            UPDATE Household
            SET Balance = (Balance - %(totalPrice)s)
            WHERE HouseHoldNum = %(householdNum)s
""",
                {"totalPrice": totalPrice, "householdNum": householdNum},
            )
            db.commit()

    def addIndex():
        myCursor.execute("""
    CREATE INDEX householdDateIDX
                         ON CampsiteBooking (HouseholdNum, StartDate)

""")

        print("Index added")

    def dropIndex():
        myCursor.execute("""
        ALTER TABLE CampsiteBooking
                         DROP INDEX householdDateIDX;
""")
        print("Index dropped")

    def testIndex():
        householdNum = int(input("Enter household number: "))
        startDate = input("Enter start date: ")

        myCursor.execute(
            """
    EXPLAIN SELECT *
                         FROM CampsiteBooking
                         WHERE HouseholdNum = %(householdNum)s
                         AND StartDate = %(startDate)s
""",
            {
                "householdNum": householdNum,
                "startDate": startDate,
            },
        )
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    endSubMenu = False
    while not endSubMenu:
        print("Select an option:")
        print("1: View all")
        print("2: Make new reservation")
        print("3: See all reservations for a household")
        print("4: See all by date")
        print("5: See average stay length by site")
        print("6: Delete a reservation")
        print("7: Add index")
        print("8: Drop index")
        print("9: Index test query")

        menuOption = int(input("Option: "))

        if menuOption == 1:
            viewAllReservations()
        elif menuOption == 2:
            makeNewReservation()
        elif menuOption == 3:
            seeHouseholdReservations()
        elif menuOption == 4:
            reservationsForDate()
        elif menuOption == 5:
            avgStayLength()
        elif menuOption == 6:
            deleteReservation()
        elif menuOption == 7:
            addIndex()
        elif menuOption == 8:
            dropIndex()
        elif menuOption == 9:
            testIndex()

        else:
            endSubMenu = True


def concessionOptions():
    def viewAllConcessions():
        myCursor.execute("""
        SELECT ItemName, Price
        FROM Concessions
        """)

        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))
     

    def buyConcession():
        try: 
            householdNum = int(input("Enter household number: "))
            itemToBuy = input("Enter the name of the item to buy: ")
            quantity = int(input("Enter the quantity to buy: "))

            db.start_transaction()
            myCursor.execute(
                """
            INSERT INTO ConcessionRecipt(HouseholdNum, ItemID, Quantity, Cost)
                            SELECT %(householdNum)s, c.ItemID, %(quantity)s, %(quantity)s * c.Price
                            FROM Concessions AS c
                            WHERE c.ItemName = %(itemToBuy)s
                            AND c.StockAvailable >= %(quantity)s

            """,
                {
                    "householdNum": householdNum,
                    "itemToBuy": itemToBuy,
                    "quantity": quantity,
                },
            )

            # Add the concession charges to the household
            myCursor.execute(
                    """
                UPDATE Household
                                INNER JOIN Concessions AS c ON c.ItemName = %(itemToBuy)s
                                SET Balance = (Balance + c.Price * %(quantity)s)
                                WHERE HouseHoldNum = %(householdNum)s
                """,
                    {"householdNum": householdNum,
                    "itemToBuy": itemToBuy,
                    "quantity": quantity},
                )

                # Update the stock available
            myCursor.execute(
                    """
                UPDATE Concessions
                SET StockAvailable = (StockAvailable - %(quantity)s)
                WHERE ItemName = %(itemToBuy)s
                """,
                    {"quantity": quantity, "itemToBuy": itemToBuy},
                )
            print("Concession puchased successfully")
            db.commit()

        except mysql.connector.Error as dbError:
            print("Error with the database: ", dbError)
            db.rollback()
        except Exception as e:
            print("There was an error: ", e)
            db.rollback()
            

    def seeStock():
        myCursor.execute("""
        SELECT ItemName, StockAvailable
                         FROM Concessions
                         ORDER BY StockAvailable;

""")

        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def viewPurchases():
        myCursor.execute("""
        SELECT * FROM ConcessionRecipt
""")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def viewPurchasesByHousehold():
        householdNum = int(input("Enter household number: "))

        myCursor.execute(""" DROP VIEW IF EXISTS PurchasesByHousehold """)

        myCursor.execute(""" CREATE VIEW PurchasesByHousehold AS
                         SELECT *
                         FROM ConcessionRecipt
                        """)

        myCursor.execute(
            """ SELECT * FROM PurchasesByHousehold
                         WHERE HouseholdNum = %(householdNum)s """,
            {"householdNum": householdNum},
        )
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def itemSaleSummary():
        myCursor.execute("""
        SELECT cr.ItemID, c.ItemName, COUNT(*) AS AmountSold, COUNT(*) * c.Price AS TotalSale
                         FROM ConcessionRecipt AS cr
                         INNER JOIN Concessions AS c ON cr.ItemID = c.ItemID
                         GROUP BY cr.ItemID, c.ItemName
                         ORDER BY AmountSold ASC, TotalSale ASC
""")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def addIndex():
        myCursor.execute(""" 
    CREATE INDEX QuantityAndCostIDX
                         On ConcessionRecipt (Quantity, Cost)
 """)

    print("Index added")

    def dropIndex():
        myCursor.execute(""" 
        ALTER TABLE ConcessionRecipt
                         DROP INDEX QuantityAndCostIDX
 """)
    print("Index Dropped")
    def testIndex():
        quantity = int(input("Enter a quantity: "))
        cost = float(input("Enter a cost: "))
        myCursor.execute(
            """  
    EXPLAIN SELECT *
                         FROM ConcessionRecipt
                         WHERE Quantity = %(quantity)s
                         AND Cost = %(cost)s
""",
            {"quantity": quantity, "cost": cost},
        )
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

    def addStock():
        try:
            itemName = input("Enter item name: ")
            addQuantity = int(input("Quantity to add: "))

            db.start_transaction()

            #Confirm that the item exists
            myCursor.execute(""" 
            SELECT ItemID
                             FROM Concessions
                             WHERE ItemName = %(itemName)s
 """,{"itemName": itemName})
            result = myCursor.fetchone()

            #End transaction if item doesn't exist
            if not result:
                print("Item doesn't exist")
                db.rollback()
                return
            
            myCursor.execute(""" SAVEPOINT preStockUpdate """)

            #Update the stock
            myCursor.execute(""" 
            UPDATE Concessions
                             SET StockAvailable = StockAvailable + %(addQuantity)s
                             WHERE ItemName = %(itemName)s

 """,{"addQuantity": addQuantity,
      "itemName": itemName})
            
            #Commit the stock update
            db.commit()

        except Exception as e:
            print("An error occured:", e)
            myCursor.execute(""" ROLLBACK TO SAVEPOINT preStockUpdate """)
            db.commit()

    endSubMenu = False
    while not endSubMenu:
        print("1: View all concessions")
        print("2: Buy concessions")
        print("3: See all purchases")
        print("4: See all concessions by household")
        print("5: See current stock")
        print("6: See sale summary of all items")
        print("7: Create index")
        print("8: Drop index")
        print("9: Index test query")
        print("10: Add to stock")
        menuOption = int(input("Option: "))

        if menuOption == 1:
            viewAllConcessions()
        elif menuOption == 2:
            buyConcession()
        elif menuOption == 3:
            viewPurchases()
        elif menuOption == 4:
            viewPurchasesByHousehold()
        elif menuOption == 5:
            seeStock()
        elif menuOption == 6:
            itemSaleSummary()
        elif menuOption == 7:
            addIndex()
        elif menuOption == 8:
            dropIndex()
        elif menuOption == 9:
            testIndex()
        elif menuOption == 10:
            addStock()
        else:
            endSubMenu = True


def mainMenu():
    # Main menu
    endMenu = False

    while not endMenu:
        print("Select an option:")
        print("1: Show Campsite reservation options")
        print("2: Concession options")
        print("3: Show all watercraft")
        print("4: Show all picnic shelters")
        print("5: Show households")
        print("6: Watercraft reservation options")
        print("7: Picnic shelter reservation options")

        menuOption = int(input("Option: "))
        if menuOption == 1:
            campsiteReservationOption()
        elif menuOption == 2:
            concessionOptions()
        elif menuOption == 3:
            showWatercraft()
        elif menuOption == 4:
            showShelters()
        elif menuOption == 5:
            showHouseholds()

        else:
            endMenu = True


def main():
    # Connect to the database
    initialize_database()

    # Display the main menu
    mainMenu()

    


if __name__ == "__main__":
    main()
