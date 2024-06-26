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

activity_body = {
    "client": "00606EFFFEAB11DB",
    "timestamp": "2020-03-01 19:18:00",
    "devices": {
        "fridge": 82.12,
        "oven": 0.0,
        "water_heater": 0.0,
        "AC": 836.41,
        "toaster": 2017.96
    },
    "occupancy": {
        "occupancy": 1.0
    }
}


activity_response = requests.post('http://127.0.0.1:8084/activity',json=activity_body).json()

print(activity_response)
