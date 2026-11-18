CREATE DATABASE IF NOT EXISTS ola_project;
USE ola_project;

DROP TABLE IF EXISTS ola_rides;

CREATE TABLE ola_rides (
    Date DATE,
    Time TIME,
    Booking_ID VARCHAR(50) PRIMARY KEY,
    Booking_Status VARCHAR(50),
    Customer_ID VARCHAR(50),
    Vehicle_Type VARCHAR(50),
    Pickup_Location VARCHAR(100),
    Drop_Location VARCHAR(100),
    V_TAT INT NULL,
    C_TAT INT NULL,
    Canceled_Rides_by_Customer VARCHAR(150) NULL,
    Canceled_Rides_by_Driver VARCHAR(150) NULL,
    Incomplete_Rides VARCHAR(10) NULL,
    Incomplete_Rides_Reason VARCHAR(150) NULL,
    Booking_Value DECIMAL(10, 2),
    Payment_Method VARCHAR(50) NULL,
    Ride_Distance INT,
    Driver_Ratings DECIMAL(3, 1) NULL,
    Customer_Rating DECIMAL(3, 1) NULL,
    Day_of_Week VARCHAR(20),
    Ride_Hour INT,
    Time_of_Day VARCHAR(20)
);

SET GLOBAL local_infile = 1;

USE ola_project;

LOAD DATA LOCAL INFILE 'C:/Users/wwero/OneDrive/Documents/Desktop/Project OLA (Labmentix)/OLA_Cleaned_July.csv'
INTO TABLE ola_rides
FIELDS TERMINATED BY ',' 
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(
    Date, Time, Booking_ID, Booking_Status, Customer_ID, Vehicle_Type, 
    Pickup_Location, Drop_Location, @V_TAT, @C_TAT, 
    @Canceled_Rides_by_Customer, @Canceled_Rides_by_Driver, 
    @Incomplete_Rides, @Incomplete_Rides_Reason, Booking_Value, 
    @Payment_Method, Ride_Distance, @Driver_Ratings, @Customer_Rating, 
    Day_of_Week, Ride_Hour, Time_of_Day
)
SET
    V_TAT = NULLIF(@V_TAT, ''),
    C_TAT = NULLIF(@C_TAT, ''),
    Canceled_Rides_by_Customer = NULLIF(@Canceled_Rides_by_Customer, ''),
    Canceled_Rides_by_Driver = NULLIF(@Canceled_Rides_by_Driver, ''),
    Incomplete_Rides = NULLIF(@Incomplete_Rides, ''),
    Incomplete_Rides_Reason = NULLIF(@Incomplete_Rides_Reason, ''),
    Payment_Method = NULLIF(@Payment_Method, ''),
    Driver_Ratings = NULLIF(@Driver_Ratings, ''),
    Customer_Rating = NULLIF(@Customer_Rating, '');
    
    
USE ola_project;

SELECT COUNT(*) AS Total_Rows FROM ola_rides;
SELECT * FROM ola_rides LIMIT 10;

USE ola_project;

-- 1. Retrieve all successful bookings
CREATE OR REPLACE VIEW Successful_Bookings AS
SELECT * 
FROM ola_rides 
WHERE Booking_Status = 'Success';

-- 2. Find the average ride distance for each vehicle type
CREATE OR REPLACE VIEW Avg_Ride_Distance_Per_Vehicle AS
SELECT Vehicle_Type, ROUND(AVG(Ride_Distance), 2) AS Avg_Distance
FROM ola_rides
GROUP BY Vehicle_Type;

-- 3. Get the total number of cancelled rides by customers
CREATE OR REPLACE VIEW Total_Customer_Cancellations AS
SELECT COUNT(*) AS Customer_Canceled_Count
FROM ola_rides
WHERE Booking_Status = 'Canceled by Customer';

-- 4. List the top 5 customers who booked the highest number of rides
CREATE OR REPLACE VIEW Top_5_Customers_By_Rides AS
SELECT Customer_ID, COUNT(Booking_ID) AS Total_Rides
FROM ola_rides
GROUP BY Customer_ID
ORDER BY Total_Rides DESC
LIMIT 5;

-- 5. Get the number of rides cancelled by drivers due to personal and car-related issues
CREATE OR REPLACE VIEW Driver_Cancellations_Personal_Car AS
SELECT COUNT(*) AS Driver_Canceled_Personal_Car
FROM ola_rides
WHERE Canceled_Rides_by_Driver = 'Personal & Car related issue';

-- 6. Find the maximum and minimum driver ratings for Prime Sedan bookings
CREATE OR REPLACE VIEW Prime_Sedan_Driver_Ratings AS
SELECT 
    MAX(Driver_Ratings) AS Max_Driver_Rating,
    MIN(Driver_Ratings) AS Min_Driver_Rating
FROM ola_rides
WHERE Vehicle_Type = 'Prime Sedan';

-- 7. Retrieve all rides where payment was made using UPI
CREATE OR REPLACE VIEW UPI_Payments AS
SELECT * 
FROM ola_rides
WHERE Payment_Method = 'UPI';

-- 8. Find the average customer rating per vehicle type
CREATE OR REPLACE VIEW Avg_Customer_Rating_Per_Vehicle AS
SELECT Vehicle_Type, ROUND(AVG(Customer_Rating), 2) AS Avg_Customer_Rating
FROM ola_rides
GROUP BY Vehicle_Type;

-- 9. Calculate the total booking value of rides completed successfully
CREATE OR REPLACE VIEW Total_Successful_Booking_Value AS
SELECT SUM(Booking_Value) AS Total_Successful_Revenue
FROM ola_rides
WHERE Booking_Status = 'Success';

-- 10. List all incomplete rides along with the reason
CREATE OR REPLACE VIEW Incomplete_Rides_List AS
SELECT Booking_ID, Incomplete_Rides_Reason
FROM ola_rides
WHERE Incomplete_Rides = 'Yes';

SELECT * FROM Avg_Ride_Distance_Per_Vehicle;
SELECT * FROM Total_Customer_Cancellations;
SELECT * FROM Top_5_Customers_By_Rides;
SELECT * FROM Driver_Cancellations_Personal_Car;
SELECT * FROM Prime_Sedan_Driver_Ratings;
SELECT * FROM Avg_Customer_Rating_Per_Vehicle;
SELECT * FROM Total_Successful_Booking_Value;





