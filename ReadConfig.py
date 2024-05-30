# -*- coding: utf-8 -*-self.apiKey
import configparser
from pathlib import Path
from datetime import datetime as dt
import logging


class ReadConfig:
    """
    Handler class for the main class config file
    """
    def __init__(self):
        self.thispath = Path("config.ini")
        self.config = configparser.ConfigParser()
        self.config.read(self.thispath)
        self.section = 'Application'
        self.type = self.config.get('Application', 'type')
        
        self.path = self.config.get('Application', 'path')
        self.timeZone = self.config.get('Application', 'timeZone')
        self.reinit_configs = self.config.getint('Application', 'reinit_configs')
        self.reinit_occupancy = self.config.getint('Application', 'reinit_occupancy')
        self.reinit_activity = self.config.getint('Application', 'reinit_activity')

        self.host = self.config.get('Api', 'host')
        self.api_port = self.config.getint('Api', 'port')
        self.debug = self.config.getboolean('Api', 'debug')
        self.threaded = self.config.getboolean('Api', 'threaded')

        self.water_heater_threshold = self.config.getint('Water Heater', 'threshold')
    # def log_timestamp(self, timestamp):
    #     # TODO UNCOMMENT
    #     try:
    #         tmstmp = dt_to_str(timestamp)
    #         # self.config.set(self.section, 'run_from', tmstmp)
    #         # self.config.write(open(self.thispath, "w"))
    #     except Exception as e:
    #         print("Exception in ReadConfig.set_field")
    #         logging.exception(e)

    def set_field(self, field, value):
        try:
            if type(value) == dt:
                value = value.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            else:
                value = str(value)
            self.config.set(self.section, field, value)
            self.config.write(open(self.thispath, "w"))
        except Exception as e:
            print("Exception in ReadConfig.set_field")
            logging.exception(e)


