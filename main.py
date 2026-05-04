"""Authors: Bryan Erickson and Aidan Adams

!!!!!!! Run 'initializeDB.py' and 'Generator.py' before using this program !!!!!!!
"""

import mysql.connector
from mysql.connector import errorcode
from tabulate import tabulate


def initialize_database():

    # Connects to the MySQL server
    try: 
        db = mysql.connector.connect(
            host="localhost", user="root", password="wordPass12", autocommit=True
        )

        myCursor = db.cursor(buffered=True)

        # Creates the database if it doesn't exist and uses it
        myCursor.execute("CREATE DATABASE IF NOT EXISTS Campground")
        myCursor.execute("USE Campground")
        myCursor.close()

    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Invalid credentials")
            return
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database not found")
            return
        else:
            print("Cannot connect to database:", err)
            return
    return db


def showHouseholds(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT * FROM Household
    """)

    rows = myCursor.fetchall()
    headers = [col[0] for col in myCursor.description]

    print(tabulate(rows, headers=headers, tablefmt="grid"))
    myCursor.close()


##Shows all shelter reservations and the households that are suing them
def showShelterReservations(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT ShelterId, HouseholdNum 
    FROM Reservations, PicnicShelters 
    WHERE HouseholdNum = HouseholdNum
    """)
    myCursor.close()


##Show all reciepts with item costs and names
def purchasedItems(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT ItemId, ItemName, Price
    FROM ConcessionRecipt, Concessions
    WHERE ItemId = ItemId
    """)
    myCursor.close()


##Shows the average price of all watercraft
def WatercraftAvg(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT WaterCraftID, AVG(Price) AS Mean_Price
    FROM Watercraft
    GROUP BY
    WaterCraftID
    """)
    myCursor.close()


##Find all households with zero or negative balance with a booked campsite
def OverDue(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT * FROM CampsiteBooking
    WHERE HouseholdNum IN (
        Select HouseholdNum FROM Household
        WHERE Balance <=0
    )
    """)
    myCursor.close()


## Find all concession receipts with cost less than price(for discounts)
def discountedItems(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT * FROM ConcessionRecipt
    WHERE Cost < (
        SELECT Price FROM Concessions
        WHERE Concessions.ItemID = ConcessionRecipt.ItemID
    )
    """)
    myCursor.close()


## Check if any item out of stock
## see if this runs later σ_{StockAvailable < 1}(Concessions)


def showWaterReservations(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT WaterCraftId, HouseholdNum FROM Reservations, Watercraft WHERE HouseholdNum = HouseholdNum
    """)
    myCursor.close()


def showWatercraft(conn):
    myCursor = conn.cursor()
    myCursor.execute("SELECT * FROM Watercraft")
    rows = myCursor.fetchall()
    headers = [col[0] for col in myCursor.description]

    print(tabulate(rows, headers=headers, tablefmt="grid"))
    myCursor.close()


def showShelters(conn):
    myCursor = conn.cursor()
    myCursor.execute("""
    SELECT * FROM PicnicShelters
    """)

    rows = myCursor.fetchall()
    headers = [col[0] for col in myCursor.description]

    print(tabulate(rows, headers=headers, tablefmt="grid"))
    myCursor.close()


def campsiteReservationOption(conn):
    def viewAllReservations(conn):
        myCursor = conn.cursor()
        myCursor.execute("SELECT * FROM CampsiteBooking")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))

        myCursor.close()

    def makeNewReservation(conn):
        try:
            myCursor = conn.cursor()
            householdNum = int(input("Enter household number: "))
            campsiteName = input("Enter campsite to book: ")
            startDate = input("Enter start date: ")
            endDate = input("Enter end date: ")

            conn.start_transaction()

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
            conn.commit()
            print("Booking added succesfully")
            myCursor.close()

        #Handles errors with the database, rolls-back transaction
        except mysql.connector.Error as dbError:
            print("Error with the database, transaction rolled-back:", dbError)
            conn.rollback()
            myCursor.close()

        #Handles any other error, rolls-back transaction
        except Exception as e:
            print("An error occured, transaction was rolled-back: ", e)
            conn.rollback()
            myCursor.close()

    def seeHouseholdReservations(conn):
        myCursor = conn.cursor()
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

    def reservationsForDate(conn):
        myCursor = conn.cursor()
        myCursor.execute("""
        SELECT * FROM CampsiteBooking
        ORDER BY StartDate ASC;
""")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))
        myCursor.close()
    def avgStayLength(conn):
        myCursor = conn.cursor()
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
        myCursor.close()

    def deleteReservation(conn):
        myCursor = conn.cursor()
        householdNum = int(input("Enter household number: "))
        startDate = input("Enter start date: ")

        conn.start_transaction()

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
            conn.rollback()
            myCursor.close()
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
            conn.commit()
            myCursor.close()

    def addIndex(conn):
        myCursor = conn.cursor()
        myCursor.execute("""
    CREATE INDEX householdDateIDX
                         ON CampsiteBooking (HouseholdNum, StartDate)

""")

        print("Index added")
        myCursor.close()

    def dropIndex(conn):
        myCursor = conn.cursor()
        myCursor.execute("""
        ALTER TABLE CampsiteBooking
                         DROP INDEX householdDateIDX;
""")
        print("Index dropped")
        myCursor.close()

    def testIndex(conn):
        myCursor = conn.cursor()
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
        myCursor.close()

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
            viewAllReservations(conn)
        elif menuOption == 2:
            makeNewReservation(conn)
        elif menuOption == 3:
            seeHouseholdReservations(conn)
        elif menuOption == 4:
            reservationsForDate(conn)
        elif menuOption == 5:
            avgStayLength(conn)
        elif menuOption == 6:
            deleteReservation(conn)
        elif menuOption == 7:
            addIndex(conn)
        elif menuOption == 8:
            dropIndex(conn)
        elif menuOption == 9:
            testIndex(conn)

        else:
            endSubMenu = True


def concessionOptions(conn):
    def viewAllConcessions(conn):
        myCursor = conn.cursor()
        myCursor.execute("""
        SELECT ItemName, Price
        FROM Concessions
        """)

        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))
        myCursor.close()

    def buyConcession(conn):
        try: 
            myCursor = conn.cursor()
            householdNum = int(input("Enter household number: "))
            itemToBuy = input("Enter the name of the item to buy: ")
            quantity = int(input("Enter the quantity to buy: "))

            conn.start_transaction()
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
            conn.commit()
            myCursor.close()

        except mysql.connector.Error as dbError:
            print("Error with the database: ", dbError)
            conn.rollback()
            myCursor.close()
        except Exception as e:
            print("There was an error: ", e)
            conn.rollback()
            myCursor.close()
            

    def seeStock(conn):
        myCursor = conn.cursor()
        myCursor.execute("""
        SELECT ItemName, StockAvailable
                         FROM Concessions
                         ORDER BY StockAvailable;
""")

        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))
        myCursor.close()

    def viewPurchases(conn):
        myCursor = conn.cursor()
        myCursor.execute("""
        SELECT * FROM ConcessionRecipt
""")
        rows = myCursor.fetchall()
        headers = [col[0] for col in myCursor.description]

        print(tabulate(rows, headers=headers, tablefmt="grid"))
        myCursor.close()

    def viewPurchasesByHousehold(conn):
        myCursor = conn.cursor()
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
        myCursor.close()

    def itemSaleSummary(conn):
        myCursor = conn.cursor()
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
        myCursor.close()

    def addIndex(conn):
        myCursor = conn.cursor()
        myCursor.execute(""" 
    CREATE INDEX QuantityAndCostIDX
                         On ConcessionRecipt (Quantity, Cost)
 """)

        print("Index added")
        myCursor.close()


    def dropIndex(conn):
        myCursor = conn.cursor()
        myCursor.execute(""" 
        ALTER TABLE ConcessionRecipt
                         DROP INDEX QuantityAndCostIDX
 """)
        print("Index Dropped")
        myCursor.close()
    
    def testIndex(conn):
        myCursor = conn.cursor()
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
        myCursor.close()

    def addStock(conn):
        try:
            myCursor = conn.cursor()
            itemName = input("Enter item name: ")
            addQuantity = int(input("Quantity to add: "))

            conn.start_transaction()

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
                conn.rollback()
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
            conn.commit()
            myCursor.close()

        except Exception as e:
            print("An error occured:", e)
            myCursor.execute(""" ROLLBACK TO SAVEPOINT preStockUpdate """)
            conn.commit()
            myCursor.close()

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
            viewAllConcessions(conn)
        elif menuOption == 2:
            buyConcession(conn)
        elif menuOption == 3:
            viewPurchases(conn)
        elif menuOption == 4:
            viewPurchasesByHousehold(conn)
        elif menuOption == 5:
            seeStock(conn)
        elif menuOption == 6:
            itemSaleSummary(conn)
        elif menuOption == 7:
            addIndex(conn)
        elif menuOption == 8:
            dropIndex(conn)
        elif menuOption == 9:
            testIndex(conn)
        elif menuOption == 10:
            addStock(conn)
        else:
            conn.close()
            endSubMenu = True
            


def mainMenu(conn):
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
            campsiteReservationOption(conn)
        elif menuOption == 2:
            concessionOptions(conn)
        elif menuOption == 3:
            showWatercraft(conn)
        elif menuOption == 4:
            showShelters(conn)
        elif menuOption == 5:
            showHouseholds(conn)

        else:
            conn.close()
            endMenu = True



def main():
    # Connect to the database
    conn = initialize_database()

    # Display the main menu
    mainMenu(conn)

if __name__ == "__main__":
    main()
