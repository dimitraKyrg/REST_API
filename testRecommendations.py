import clips.agenda
import clips.common
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import time
import datetime 
from durable.lang import *
from durable.lang import post
from simple_speech import Speech
from durable.lang import *
from durable.lang import ruleset, when_all, assert_fact, c, m
from durable_rules_tools.rules_utils import new_ruleset, Set, Subject
import clips
from multiprocessing import Process, Queue
import sqlDB
import re

current_time = datetime.datetime.now()

'''
    declaration of json variables for when using the post method in Api's endpoints.
'''
create_activity_models_body = {
    "client": "00606EFFFEABADEF",
    "training_set": {
        "fridge": [
            ["2021-10-19 08:59:00", 700.0],
            ["2021-10-19 09:00:00", 750.0],
      
            ["2021-10-19 10:50:00", 800.0]
        ],
        "oven": [
            ["2021-10-19 08:59:00", 700.0],
            ["2021-10-19 09:00:00", 750.0],
      
            ["2021-10-19 10:50:00", 800.0]
        ]
      }
  }

savings_body = {
    "timestamp": "2020-03-01 17:10:00",
    "client": "00606EFFFEAB11DB",
    "number": 6,
    "sent_at": "2020-03-01 16:10:00",
    "setTemp": 21.0,
    "power_interval": 1,

    "power": [
        ["2020-01-01 00:00:00", 700.0],
        ["2020-01-01 00:01:00", 637.0],
        ["2020-01-01 00:02:00", 749.0],
        ["2020-01-01 00:03:00", 717.0],
        ["2020-01-01 00:04:00", 787.0],
        ["2020-01-01 00:05:00", 741.0],
    
        ["2020-01-01 00:59:00", 643.0],
        ["2020-01-01 01:00:00", 628.0]
    ],
    
    "power": [
        ["2022-02-03 10:00:00", 22.0, 2],
        ["2022-02-03 10:01:00", 22.0, 2],
        ["2022-02-03 10:02:00", 22.0, 2],
        ["2022-02-03 10:03:00", 22.0, 2],

        ["2022-02-03 12:40:00", 22.0, 2]
    ],
    
        "power": [
        ["2022-02-03 10:00:00", 22.5, 1],
        ["2022-02-03 10:01:00", 22.5, 1],
        ["2022-02-03 10:02:00", 22.5, 1],
        ["2022-02-03 10:03:00", 22.5, 1],
    
        ["2022-02-03 12:40:00", 22.5, 1]
    ]
    }

occupancy_retrain_body = {
	"client": "00606EFFFEABADEF",
	"training_set": {
		"occupancy": [
			["2021-10-19 08:59:00", 0],
			["2021-10-19 09:00:00", 1],

			["2021-10-19 10:50:00", 2]
		],
		"mains_power": [
			["2021-10-19 08:59:00", 700.0],
			["2021-10-19 09:00:00", 750.0],

			["2021-10-19 10:50:00", 800.0]
		]
	}
}

occupancy_correction_body = {
	"client": "00606EFFFEABADEF",
	"timestamp": "2021-10-19 08:59:41",
	"occupancy": [
			["2021-10-19 08:59:00", 0],
			["2021-10-19 09:00:00", 1],

			["2021-10-19 10:50:00", 2]
        ]
}

activity_correction_body = {
    "client": "00606EFFFEABADEF",
    "devices": {
        "fridge": {
            "activity": [
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 10:50:00", 0],
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 1],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 10:50:00", 0],
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 10:50:00", 0],
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 10:50:00", 0],
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 1],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 10:50:00", 0],
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 09:00:00", 0],
                ["2021-10-19 10:50:00", 0]
            ]
        },
        "oven": {
            "activity": [
                ["2021-10-19 08:59:00", 0],
                ["2021-10-19 09:00:00", 1],
                ["2021-10-19 09:00:00", 1]
            ]
        }
    }
}

vcl_train_body = {
    "client": "00606EFFFEABADEF",
	"training_set": [
		["2021-10-19 08:59:00", 700.0, 100.0, 1.322, 90, 1],
		["2021-10-19 09:00:00", 750.0, 100.0, 1.324, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 100.0, 1.324, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 100.0, 1.324, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 200.0, 1.324, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 130.0, 1.3254, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 100.0, 1.324, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 110.0, 1.324, 90, 1],
        ["2021-10-19 09:00:00", 750.0, 100.0, 1.324, 90, 1],
		["2021-10-19 10:50:00", 800.0, 105.0, 1.400, 90, 1]
	]
}

tch_train_body = {
	"client": "00606EFFFEABADEF",
	"training_set": [
		["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 3, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-3, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-2, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 1, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3,-1, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 3, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-3, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-2, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 1, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3,-1, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 3, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-3, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-2, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 1, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3,-1, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 3, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-3, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-2, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 1, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3,-1, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 3, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-3, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 2, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3,-2, 25.0, 23.0, 1],
        ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 1, 25.0, 23.0, 1],
		["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3,-1, 25.0, 23.0, 1],
		["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 0, 25.0, 23.0, 1],

	]
}


def simulateSensors(client):
    """
    This is a temporary function to simulate taking measurements from sensors. Instead of taking the measurements, it asks for them as keyboard input for now.

    arguments:
    ----------
    client          -- client for which measurements will be taken

    output:
    --------
    sensor_dict     -- dictionary with measurements from all sensors and the timestamp

    """
    current_time = str(datetime.datetime.now())
    latitude = input("latitude? ")
    longitude = input("longitude? ")
    hvac_temperature = input("hvac_temperature? ")
    hvac_humidity = input("hvac_humidity? ")
    hvac_luminance = input("hvac_luminance? ")
    sensor_temperature = input("sensor_temperature? ")
    sensor_humidity = input("sensor_humidity? ")
    sensor_luminance = input("sensor_luminance? ")
    co2 = input("co2? ")
    water_heater = input("water_heater? (on/off)  ")

    sensor_dict = {'timestamp' : current_time[0:19],'latitude':latitude,'longtitude':longitude,'hvac_temperature':hvac_temperature,'hvac_humidity':hvac_humidity,'hvac_luminance':hvac_luminance,
                   'sensor_temperature':sensor_temperature,'sensor_humidity':sensor_humidity,'sensor_luminance':sensor_luminance,'Co2':co2,'client':client,'water_heater':water_heater}

    return sensor_dict

def collectRecommendations(sensor_dict):
    """
    This function takes as input measurements from the sensors runs all necessary AI models and returns numbers of recommendations .

    arguments:
    ----------
    sensor_dict             -- dictionary with measurements from sensors 

    output:
    --------
    recommendationNumbers   -- list with all recommendations

    """

    # get thermal and visual comfort from hvac and sensor
    comfort_body = {
            "client": sensor_dict['client'],
            "timestamp": sensor_dict['timestamp'],
            "latitude": 37.999545,
            "longitude": 23.746887,
            "devices": {
                "hvac": {
                    "temperature": sensor_dict['hvac_temperature'],
                    "humidity": sensor_dict['hvac_humidity'],
                    "luminance": sensor_dict['hvac_luminance']
                },
                "sensor": {
                    "temperature": sensor_dict['sensor_temperature'],
                    "humidity": sensor_dict['sensor_humidity'],
                    "luminance": sensor_dict['sensor_luminance']
                }
            }
    }
    comfort_response = requests.post('http://127.0.0.1:8084/comfort',json=comfort_body)
    comfort_keys = ['hvac','sensor']
    comfort_dict = {x:comfort_response.json()[x] for x in comfort_keys}

    # get occupancy info
    occupancy_body = {
    "client": sensor_dict['client'],
    "timestamp": sensor_dict['timestamp'],
    "consumption": 2024.0,
    "manager_data": {
        "feedback": {
            "presence": 0,
            "timestamp": sensor_dict['timestamp']
        },
        "geofencing": {
            "latitude": 38.041061,
            "longitude": 23.744697,
            "timestamp": sensor_dict['timestamp']
        },
        "scheduler": {
            "presence": 0,
            "timestamp": sensor_dict['timestamp']
        },
        "sensor": {
            "presence": 0,
            "timestamp": sensor_dict['timestamp']
        },
            "smartplug": {
            "presence": 0,
            "timestamp": sensor_dict['timestamp']
        }
    }
}
    occupancy_response = requests.post('http://127.0.0.1:8084/occupancy',json=occupancy_body).json()
    occupancy = occupancy_response['occupancy']

    # get disaggregation info
    disaggregation_body = {
    "client": "00606EFFFEABADEF",
    "devices": [
        "fridge",
        "oven",
        "water_heater",
        "AC",
        "iron",
        "toaster"
    ],
    "power_list": [
        ["2020-03-01 19:14:00", 2024.0, 294.0],
        ["2020-03-01 19:15:00", 2026.0, 294.0],
        ["2020-03-01 19:16:00", 2026.0, 294.0],
        ["2020-03-01 19:17:00", 2026.0, 294.0],
        ["2020-03-01 19:18:00", 2024.0, 294.0],
        ["2020-03-01 19:19:00", 2025.0, 294.0]
    ]
    }
    disaggregation_response = requests.post('http://127.0.0.1:8084/disaggregation',json=disaggregation_body)
    devices = disaggregation_response.json()
    exclude_keys = ['timestamp']
    new_devices = {k: devices[k] for k in set(list(devices.keys())) - set(exclude_keys)}

    # override occupancy so that it works for now
    occupancy = 1

    # get activity info (boolean value for each device)
    activity_body = {
        "client": sensor_dict['client'],
        "timestamp": sensor_dict['timestamp'],
        "devices": new_devices,
        "occupancy": {
            "occupancy": occupancy
        }
    }   
    activity_response = requests.post('http://127.0.0.1:8084/activity',json=activity_body).json()
    AC_activity, coffee_maker_activity, dishwasher_activity, fridge_activity, hair_dryer_activity, microwave_activity,oven_activity, toaster_activity, washing_machine_activity, water_heater_activity = 0,0,0,0,0,0,0,0,0,0

    for key, value in activity_response.items():
        locals()[key] = value 

    # create the json that will be used with the post method in the recommendation endpoint
    recommendation_body = {
        "timestamp": sensor_dict['timestamp'],
        "client": "00606EFFFEAB11DB",
        "reinitialize_recommendations": False,
        "devices": new_devices,
        "water_heater": {
            "heater_1": [
                ["2020-01-01 00:00:00", 700.0],
                ["2020-01-01 00:01:00", 635.0],
                ["2020-01-01 00:58:00", 718.0],
                ["2020-01-01 00:59:00", 607.0]
            ],
            "heater_2": [
                ["2020-01-01 00:00:00", 700.0],
                ["2020-01-01 00:01:00", 635.0],
                ["2020-01-01 00:58:00", 718.0],
                ["2020-01-01 00:59:00", 607.0]
            ]
        },
        "night_power_discount": False,
        "co2_threshold": 200,
        "humidity_threshold": 10,
        "comfort": comfort_dict,
        "occupancy": {
            "60": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "60-90": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        },
        "activity": {
            "fridge": fridge_activity,
            "oven": oven_activity,
            "water_heater": water_heater_activity,
            "AC": AC_activity
        },
        "weather": {
            "temperature": 25.00,
            "humidity": 40.00,
            "ghi": 600
        },
        "indoorConditions": {
            "temperature": sensor_dict['sensor_temperature'],
            "humidity": sensor_dict['sensor_humidity'],
            "luminance": sensor_dict['sensor_luminance'],
            "co2": sensor_dict['Co2']
        },
        "hvac": {
            "set_temp": sensor_dict['hvac_temperature'],
            "status": 3
        },
        "lighting": {
            "1": {
                "luminance": sensor_dict['sensor_luminance'],
                "visual_comfort": comfort_dict['sensor']['visual_comfort'],
                "dimmer": sensor_dict['hvac_luminance'],
                "status": 1
            },
            "2": {
                "luminance": 600,
                "visual_comfort": comfort_dict['sensor']['visual_comfort'],
                "dimmer": 90,
                "status": 1
            }
        },
        "thermostat": {
            "set_temp": 40.00,
            "status": 1
        },
        "generic_upper_hvac": False,
        "generic_lower_hvac": False,
        "generic_upper_thermostat": False,
        "generic_lower_thermostat": False,
        "generic_turn_off_standby": False,
        "generic_open_windows": False,
        "generic_change_setpoint": False,
        "generic_efficient_heating": False,
        "aggregate_savings": [
            [1000.0, 1],
            [2234.1, 0],
            [3122.7, 1],
            [4841.1, 1],
            [500.9, 0]
        ],
        "weekly_smartplugs": {
            "plug_name_1": {
                "current_week": 3.5,
                "previous_week": 3.0
            },
            "plug_name_2": {
                "current_week": 5.5,
                "previous_week": 2.3
            },
            "plug_name_3": {
                "current_week": 8,
                "previous_week": 2
            }
        },
        "weekly_consumption": {
            "current_week": 9,
            "previous_week": 8.1
        }
    }
    
    # get recommendation info
    recommendation_response = requests.post('http://127.0.0.1:8084/recommendation',json=recommendation_body).json()
    recomedtationList = recommendation_response['recommendations']
    recommendationNumbers = []
    recommendationMessages = []

    for rec in recomedtationList:
        recNumb = rec['number']
        recommendationNumbers.append(recNumb)
        recMess = rec['message']
        recommendationMessages.append(recMess)

    print(recommendationNumbers)
    print(recommendationMessages)

    return recommendationNumbers


def getRecommendations(q,dbDict):
    """
    This function is called repetively in a time interval specified in the scheduler declaration. First, it calls the function simulate sensors to take sensor mesurements. 
    Then, writes in an sql database the measurements and the timestamp. Then, uses these measurements to feed the ai models and get recommendations.

    arguments:
    ----------
    q               -- it is a queue object used to share variables between threads (processes) 
    dbDict          -- dictionary with all info to connect to mysql database

    output:
    --------
    recommendationNumbers   -- list with all recommendations

    """
    # take measurements from all sensors
    sensorDict_before = simulateSensors("00606EFFFEABADEF")
    # place measurements in an sql database
    sqlDB.addRowToDatabase(dbName = dbDict['dbName'],host = dbDict['host'], user = dbDict["user"], port = dbDict['port'], password = dbDict['password'],rowDict = sensorDict_before)

    # run ai to get recommendations
    recommendationNumbers = collectRecommendations(sensorDict_before)

    # q is a queue. It is used as a pipe between processes. 
    # In this case it is used to pass the list of activated recommendations from the first process to the second.
    q.put(recommendationNumbers)

def checkRecommendations(q,dbDict,envi):
    """
    This function is called repetively in a specific exact time interval after "getRecommendations".  First, pops out the list of activated recommendations from the q queue.
    Then it takes new measurements using simulate sensors again and writes them in the sql database. 

    arguments:
    ----------
    q                           -- it is a queue object used to share variables between threads (processes) 
    dbDict                      -- dictionary with all info to connect to mysql database
    envi                        -- the rule environment as input, it is taken as input in the function so that it can be reset

    output:
    --------
    followedRecommendations     -- list of numbers of recommendations that were followed by the user
    dismissedRecommendations    -- list of numbers of recommendations that were dismissed

    """
    # reset the rule environment to delete previous facts and activations
    envi.reset()

    # extract measurements from previous timestamp from database
    sensorDict_before = sqlDB.extractLastRowFromDatabase(dbName = dbDict['dbName'],host = dbDict['host'], user = dbDict["user"], port = dbDict['port'], password = dbDict['password'])

    # the list with activated recommendations pops out of the que, now the queue is empty and this fuction knows which recommendations were activated
    recommendationNumbers = q.get()
    # get sensor measurements and write them in the database
    sensorDict_after = simulateSensors("00606EFFFEABADEF")
    sqlDB.addRowToDatabase(dbName = dbDict['dbName'],host = dbDict['host'], user = dbDict["user"], port = dbDict['port'], password = dbDict['password'],rowDict = sensorDict_after)

    # temprarily add some recommendation numbers just to check rules in the next step
    recommendationNumbers = recommendationNumbers + [1,2,3,4]

    # place recommendation facts in rule environment
    for recommendationNumber in recommendationNumbers:
        envi.assert_string(f"(Number{recommendationNumber} was recommended)")

    # place sensor facts in rule environment
    for key in sensorDict_before:
        envi.assert_string(f"({key}_before {sensorDict_before[key]})")

    for key in sensorDict_after:
        envi.assert_string(f"({key}_after {sensorDict_after[key]})")

    # run the rules
    envi.run()

    # select all facts after running the rules
    facts = []
    for i in range(len(list(envi._facts.facts()))):
        facts.append(str(list(envi._facts.facts())[i])[1:-1])
    print(facts)

    # isolate only facts that refer to execution of recommendations
    followedRecommendations = []
    dismissedRecommendations = []
    for fact in facts:
        if re.match(r"Number[\d]+ was dismissed", fact) != None:
            index = fact.find(' ')
            number = fact[6:index]
            followedRecommendations.append(int(number))
        elif re.match(r"Number[\d]+ was followed", fact) != None:
            index = fact.find(' ')
            number = fact[6:index]
            dismissedRecommendations.append(int(number))

    print(followedRecommendations)
    print(dismissedRecommendations)

    

    return followedRecommendations,dismissedRecommendations

'''
-------------------------------------------------------------------------Here variables and schedulers are being declared-------------------------------------------------------------------------
'''
# create the queue object, which will be used to share variables between processes.
q = Queue()

# create database
databaseName = "fysikoAerio8"
dbDictionary = {"host":"127.0.0.1","port" : '3306',"user" : "root","password":"my-secret-pw","dbName" : databaseName}
sqlDB.createSqlDatabase(dbName = dbDictionary['dbName'],host = dbDictionary['host'], user = dbDictionary["user"], port = dbDictionary['port'], password = dbDictionary['password'])

# create the rule environment
env = clips.Environment()

# set conflict strategy : strategy according to which newly activated rules are 
# placed in the stack of rules to be executed. BREADTH strategy is used.
# BREADTH = Newly activated rules are placed below all rules of the same salience
# Rules that are activated 
env.strategy = clips.Strategy.BREADTH

# check the used strategy is indeed the chosen one.
print(env._agenda.strategy)

# add the rules from file to the environment
env.clear()
rule_file = 'rules.CLP'
env.load(rule_file)

# Create a scheduler
scheduler = BackgroundScheduler({'apscheduler.job_defaults.max_instances': 50})
# Add the job to the scheduler - runs the 'getRecommendations' function every 00 minute
scheduler.add_job(getRecommendations, 'cron', minute="20",args=[q,dbDictionary])
# Add the job to the scheduler - runs the 'checkRecommendations' function every 15 minute
scheduler.add_job(checkRecommendations, 'cron', minute="21",args=[q,dbDictionary,env])
# Start the scheduler
scheduler.start()

'''
    In this function a cronlike scheduler is used to schedule two processes.
    The first is getRecommendtions where data is selected from sensors, ai models run and some recommendations that will be sent to the user result. This is scheduled in 00 minute
    The second is checkRecommendations 

'''
if __name__ == '__main__':

    while(1):
        time.sleep(1)
