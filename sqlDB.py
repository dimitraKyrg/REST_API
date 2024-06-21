import mysql.connector
import pandas as pd

'''
    This file contains functions used to create read and write from an sql database
'''

def createSqlDatabase(dbName,host,user,port,password):
    '''  
    arguments:
    ----------
        dbName                          -- name of the database
        host, user, port, password      --  mySql server info

    output:
    --------
        none           

        This function creates the database in the location specified by the arguments
    '''
    # connect to mySql server
    mydb = mysql.connector.connect(
        host = host,
        port = port,
        user = user,
        password=password,
    )

    # create a cursor and the database 
    mycursor = mydb.cursor()
    mycursor.execute(f"CREATE DATABASE {dbName}")

    # connect to the created database
    mydb = mysql.connector.connect(
        host = host,
        port = port,
        user = user,
        password = password,
        database = dbName
    )

    # create new cursor now that we are connected to the specific database
    mycursor = mydb.cursor()

    # create table for sensor measurements 
    mycursor.execute("""CREATE TABLE sensorMeasurements(
                        timestamp CHAR(19) NOT NULL PRIMARY KEY,
                        latitude INT,
                        longtitude INT,
                        hvac_temperature INT,
                        hvac_humididty INT,
                        hvac_luminance INT,
                        sensor_temperature INT,
                        sensor_humididty INT,
                        sensor_luminance INT,
                        Co2 INT,
                        water_heater VARCHAR(3)
                    )""")

def addRowToDatabase(dbName,host,user,port,password,rowDict):
    '''  
    arguments:
    ----------
        dbName                          -- name of the database
        host, user, port, password      --  mySql server info
        rowDict                         -- the row that will be added in a dictionary form

    output:
    --------
        none           

        This function adds one row to the database
    '''
    # connect to the created database
    mydb = mysql.connector.connect(
        host = host,
        port = port,
        user = user,
        password = password,
        database = dbName
    )

    # create a cursor
    mycursor = mydb.cursor()

    functionsTemplate = "INSERT INTO sensorMeasurements (timestamp,latitude,longtitude,hvac_temperature,hvac_humididty,hvac_luminance,sensor_temperature,sensor_humididty,sensor_luminance,Co2,water_heater) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"

    functionsInfo = [(rowDict['timestamp'],rowDict['latitude'],rowDict['longtitude'],rowDict['hvac_temperature'],rowDict['hvac_humidity'],rowDict['hvac_luminance'],rowDict['sensor_temperature'],rowDict['sensor_humidity'],rowDict['sensor_luminance'],rowDict['Co2'],rowDict['water_heater'])]

    mycursor.executemany(functionsTemplate,functionsInfo)

    mydb.commit()

# edv na to xvrisv se duo functions, to ena na pairnei olh th bash (h estv kapoiew teleytaies times an ginei terastia) kai to allo na apomonvnei thn teleytaia seira
def extractRowsFromDatabase(dbName,host,user,port,password):
    mydb = mysql.connector.connect(
        host = host,
        port = port,
        user = user,
        password = password,
        database = dbName
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM sensorMeasurements")
    myresult = mycursor.fetchall()
    result_dataFrame = pd.read_sql("SELECT * FROM sensorMeasurements", mydb)

    lastRow = result_dataFrame.iloc[-1]
    lastRowDict = lastRow.to_dict()

    return lastRowDict