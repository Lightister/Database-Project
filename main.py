"""Authors: Bryan Erickson and Aidan Adams

!!!!!!! Run 'initializeDB.py' and 'Generator.py' before using this program !!!!!!!
"""

import mysql.connector


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
    myCursor.execute(
        """
    SELECT * FROM Household
    """
    )

    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)


def showWaterReservations():
    myCursor.execute(
        """
    SELECT WaterCraftId, HouseholdNum FROM Reservations, Watercraft WHERE HouseholdNum = HouseholdNum
    """
    )


def showWatercraft():
    myCursor.execute("SELECT * FROM Watercraft")
    myResult = myCursor.fetchall()

    for x in myResult:
        print(x)


def showShelters():
    myCursor.execute(
        """
    SELECT * FROM PicnicShelters
    """
    )

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
        householdNum = int(input("Enter household number: "))
        campsiteName = input("Enter campsite to book: ")
        startDate = input("Enter start date: ")
        endDate = input("Enter end date: ")

        db.start_transaction()
        myCursor.execute(
            """
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
                        

                        """,
            {
                "householdNum": householdNum,
                "campsiteName": campsiteName,
                "startDate": startDate,
                "endDate": endDate,
            },
        )

        if myCursor.rowcount == 0:
            print("There was an error when booking, your booking was not entered.")
            db.rollback()
        else:
            # Update the household's balance
            print("Booking added successfully")
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
        myResult = myCursor.fetchall()

        for x in myResult:
            print(x)

    def reservationsForDate():
        myCursor.execute(
            """
        SELECT * FROM CampsiteBooking
        ORDER BY StartDate ASC;
"""
        )
        myResult = myCursor.fetchall()

        for x in myResult:
            print(x)

    def avgStayLength():
        myCursor.execute(
            """
        SELECT cb.CampsiteID, c.SiteName, AVG(cb.NumOfNightsBooked) AS AvgNightsBooked
        FROM CampsiteBooking AS cb
        INNER JOIN Campsite AS c ON cb.CampsiteID = c.CampsiteID
        GROUP BY cb.CampsiteID, c.SiteName
        ORDER BY AvgNightsBooked ASC;

"""
        )
        myResult = myCursor.fetchall()

        for x in myResult:
            print(x)

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

    endSubMenu = False
    while not endSubMenu:
        print("Select an option:")
        print("1: View all")
        print("2: Make new reservation")
        print("3: See all reservations for a household")
        print("4: See all by date")
        print("5: See average stay length by site")
        print("6: Delete a reservation")
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
        else:
            endSubMenu = True


def concessionOptions():
    def viewAllConcessions():
        myCursor.execute(
            """
        SELECT ItemName, Price
        FROM Concessions
        """
        )
        myResult = myCursor.fetchall()
        for x in myResult:
            print(x)

    def buyConcession():
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

        if myCursor.rowcount == 0:
            print("There was an error, no items have been purchased")
            db.rollback()
        else:
            print("Concession puchased successfully")

            # Add the concession charges to the household
            myCursor.execute(
                """
            UPDATE Household
                            INNER JOIN Concessions AS c
                            SET Balance = (Balance + c.Price * %(quantity)s)
                             WHERE HouseHoldNum = %(householdNum)s
            """,
                {"householdNum": householdNum, "quantity": quantity},
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

            db.commit()

    def seeStock():
        myCursor.execute(
            """
        SELECT ItemName, StockAvailable
                         FROM Concessions
                         ORDER BY StockAvailable ASC;

"""
        )
        myResult = myCursor.fetchall()
        for x in myResult:
            print(x)

    def viewPurchases():
        myCursor.execute(
            """
        SELECT * FROM ConcessionRecipt
"""
        )
        myResult = myCursor.fetchall()
        for x in myResult:
            print(x)

    def viewPurchasesByHousehold():
        householdNum = int(input("Enter household number: "))
        myCursor.execute(
            """
        SELECT * FROM ConcessionRecipt
                         WHERE HouseholdNum = %(householdNum)s
""",
            {"householdNum": householdNum},
        )
        myResult = myCursor.fetchall()
        for x in myResult:
            print(x)

    def itemSaleSummary():
        myCursor.execute(
            """
        SELECT cr.ItemID, c.ItemName, COUNT(*) AS AmountSold, COUNT(*) * c.Price AS TotalSale
                         FROM ConcessionRecipt AS cr
                         INNER JOIN Concessions AS c ON cr.ItemID = c.ItemID
                         GROUP BY cr.ItemID, c.ItemName
                         ORDER BY AmountSold ASC, TotalSale ASC
"""
        )
        myResult = myCursor.fetchall()
        for x in myResult:
            print(x)

    endSubMenu = False
    while not endSubMenu:
        print("1: View all concessions")
        print("2: Buy concessions")
        print("3: See all purchases")
        print("4: See all concessions by household")
        print("5: See current stock")
        print("6: See sale summary of all items")
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
        else:
            endSubMenu = True


def mainMenu():
    # Main menu
    endMenu = False

    while not endMenu:
        print("Select an option:")
        print("1: Show Campsite reservationoptions")
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
