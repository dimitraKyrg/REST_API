import sqlDB

#sqlDB.createSqlDatabase(host="127.0.0.1",port = '3306',user = "root",password="my-secret-pw",dbName="name15")
'''
rowDict = {'timestamp': "2020-03-01 19:14:00",
           'latitude' :12.5,
           'longtitude':34.6,
           'hvac_temperature': 34,
           'hvac_humididty':60,
           'hvac_luminance':50,
           'sensor_temperature' :35,
           'sensor_humididty':61,
           'sensor_luminance':120,
           'Co2':23,
           'water_heater': "on"}

sqlDB.addRowToDatabase(host="127.0.0.1",port = '3306',user = "root",password="my-secret-pw",dbName="name15",rowDict = rowDict)
'''
sqlDB.extractRowsFromDatabase(host="127.0.0.1",port = '3306',user = "root",password="my-secret-pw",dbName="name15")