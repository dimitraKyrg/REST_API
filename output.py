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
#import numpy.distutils

speaker = Speech()

EVENTRULESET = new_ruleset()
with ruleset(EVENTRULESET):
    # this rule will trigger as soon as three events match the condition
    @when_all(m.color=='red')
    def see_red(c):
        speaker.say(f'I see red')
        c.assert_fact({'status': 'danger'})
        
    @when_all(m.color!='red')
    def not_red(c):
        speaker.say(f'I see {c.m.color}')
        c.assert_fact({'status': 'safe'})

    @when_all( m.status == 'danger')
    def dangerous(c):
        speaker.say(f'That is dangerous.')
        c.retract_fact({'status': 'danger'})
        
    @when_all( m.status == 'safe')
    def safe(c):
        speaker.say(f'That is safe.')
        c.retract_fact({'status': 'safe'})

def trial(url='http://127.0.0.1:8084/comfort'):
    #s = requests.Session()
    dictionary = {
    "client": "00606EFFFEABADEF",
    "timestamp": "2020-03-01 19:18:00",
    "latitude": 37.999545,
    "longitude": 23.746887,
    "devices": {
        "hvac": {
            "temperature": 29.00,
            "humidity": 40.00,
            "luminance": 800
        },
        "sensor": {
            "temperature": 31.00,
            "humidity": 45.00,
            "luminance": 100
        }
    }
    }


    response = requests.post(url,json=dictionary)

    print(response.json())

current_time = datetime.datetime.now()

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

occupancy_body = {
    "client": "00606EFFFEAB11DB",
    "timestamp": "2020-03-01 19:18:00",
    "consumption": 2024.0,
    "manager_data": {
        "feedback": {
            "presence": 0,
            "timestamp": "2020-03-01 19:00:00"
        },
        "geofencing": {
            "latitude": 38.041061,
            "longitude": 23.744697,
            "timestamp": "2020-03-01 19:00:00"
        },
        "scheduler": {
            "presence": 0,
            "timestamp": "2020-03-01 19:00:00"
        },
        "sensor": {
            "presence": 0,
            "timestamp": "2020-03-01 19:00:00"
        },
            "smartplug": {
            "presence": 0,
            "timestamp": "2020-03-01 19:00:00"
        }
    }
}

comfort_body = {
            "client": "00606EFFFEABADEF",
            "timestamp": "2020-03-01 19:18:00",
            "latitude": 37.999545,
            "longitude": 23.746887,
            "devices": {
                "hvac": {
                    "temperature": 29.00,
                    "humidity": 40.00,
                    "luminance": 800
                },
                "sensor": {
                    "temperature": 31.00,
                    "humidity": 45.00,
                    "luminance": 100
                }
            }
}

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


def collectData():

    current_time = str(datetime.datetime.now())

    # get comfort info
    comfort_body = {
            "client": "00606EFFFEABADEF",
            "timestamp": current_time,
            "latitude": 37.999545,
            "longitude": 23.746887,
            "devices": {
                "hvac": {
                    "temperature": 29.00,
                    "humidity": 40.00,
                    "luminance": 800
                },
                "sensor": {
                    "temperature": 31.00,
                    "humidity": 45.00,
                    "luminance": 100
                }
            }
    }
    comfort_response = requests.post('http://127.0.0.1:8084/comfort',json=comfort_body)
    comfort_keys = ['hvac','sensor']
    comfort_dict = {x:comfort_response.json()[x] for x in comfort_keys}

    # get occupancy info
    occupancy_response = requests.post('http://127.0.0.1:8084/occupancy',json=occupancy_body).json()
    occupancy = occupancy_response['occupancy']

    # get disaggregation info
    disaggregation_response = requests.post('http://127.0.0.1:8084/disaggregation',json=disaggregation_body)
    devices = disaggregation_response.json()
    exclude_keys = ['timestamp']
    new_devices = {k: devices[k] for k in set(list(devices.keys())) - set(exclude_keys)}

    # override occupancy so that it works for now
    occupancy = 1

    #get activity info
    activity_body = {
        "client": "00606EFFFEABADEF",
        "timestamp": "2020-03-01 19:18:00",
        "devices": new_devices,
        "occupancy": {
            "occupancy": occupancy
        }
    }
    
    activity_response = requests.post('http://127.0.0.1:8084/activity',json=activity_body).json()
    AC, coffee_maker, dishwasher, fridge, hair_dryer, microwave,oven, toaster, washing_machine, water_heater = 0,0,0,0,0,0,0,0,0,0

    for key, value in activity_response.items():
        locals()[key] = value 

    # get recommendations 
    recommendation_body = {
        "timestamp": "2020-03-01 19:18:00",
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
            "fridge": 1,
            "oven": 0,
            "water_heater": 0,
            "AC": 1
        },
        "weather": {
            "temperature": 25.00,
            "humidity": 40.00,
            "ghi": 600
        },
        "indoorConditions": {
            "temperature": 21.00,
            "humidity": 80.00,
            "luminance": 800,
            "co2": 150
        },
        "hvac": {
            "set_temp": 39.00,
            "status": 3
        },
        "lighting": {
            "1": {
                "luminance": 400,
                "visual_comfort": 1.322,
                "dimmer": 80,
                "status": 1
            },
            "2": {
                "luminance": 600,
                "visual_comfort": 1.201,
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
    recommendation_response = requests.post('http://127.0.0.1:8084/recommendation',json=recommendation_body)
    print(recommendation_response.json())

'''
# Create a scheduler
scheduler = BackgroundScheduler()
# Add the job to the scheduler - runs the 'job' function every minute
scheduler.add_job(collectData, 'interval', minutes=0.5)
# Start the scheduler
scheduler.start()
'''

if __name__ == '__main__':
    #response= requests.post('http://127.0.0.1:8084/create_activity_models',json=create_activity_models_body)
    #response= requests.post('http://127.0.0.1:8084/savings',json=savings_body)
    #activity_response = requests.post('http://127.0.0.1:8084/activity',json=activity_body)
    #comfort_response = requests.post('http://127.0.0.1:8084/comfort',json=comfort_body)
    #recommendation_response = requests.post('http://127.0.0.1:8084/recommendation',json=recommendation_body)
    #occupancy_response = requests.post('http://127.0.0.1:8084/occupancy',json=occupancy_body)
    #disaggregation_response = requests.post('http://127.0.0.1:8084/disaggregation',json=disaggregation_body)
    #savings_response = requests.post('http://127.0.0.1:8084/savings',json=savings_body)
    #occupancy_retrain_response = requests.post('http://127.0.0.1:8084/occupancy_retrain',json=occupancy_retrain_body)
    #occupancy_correction_response = requests.post('http://127.0.0.1:8084/occupancy_correction',json=occupancy_correction_body)
    #activity_correction_response = requests.post('http://127.0.0.1:8084/activity_correction',json=activity_correction_body)
    #vcl_train_response = requests.post('http://127.0.0.1:8084/vcl_train',json=vcl_train_body)
    #tch_train_response = requests.post('http://127.0.0.1:8084/tch_train',json=tch_train_body)
    #print(occupancy_response.json())
    #print(activity_response.json())
    collectData()

    temerature = input("get temperature from sensor: ")
    humidity = input("get humidity from sensor: ")
    luminance = input("get luminance from sensor: ")

    #post(EVENTRULESET, {'temperature_before': 'red','temperature_after': 'red','humidity_before': 'red','humidity_after': 'red','luminance_before': 'red','luminance_after': 'red' , 'rule proposed' : 5})
    post(EVENTRULESET, {'color': 'green'})

    #while True:
    #    time.sleep(1)
    #    #scheduler.shutdown(wait=False)







