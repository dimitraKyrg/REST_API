import pandas as pd
import pickle
import logging
from datetime import datetime as dt, timedelta as delta
from geopy.distance import geodesic


class OccupancyManager:
    """
    The main class of the Occupancy Manager. It is the entry point that
    executes the Occupancy manager when called to decide current occupancy.
    """
    def __init__(self, args, dateto):
        try:
            self.date = dateto
            # self.client_json = client_json

            if "feedback" in args.keys():
                self.feedback = args["feedback"]
            else:
                self.feedback = None

            if "geofencing" in args.keys():
                self.geofencing = args["geofencing"]
                self.latitude = self.geofencing["latitude"]
                self.longitude = self.geofencing["longitude"]
            else:
                self.geofencing = None

            if "scheduler" in args.keys():
                self.scheduler = args["scheduler"]
            else:
                self.scheduler = None

            if "sensor" in args.keys():
                self.sensor = args["sensor"]
            else:
                self.sensor = None

            if "smartplug" in args.keys():
                self.smartplug = args["smartplug"]
            else:
                self.smartplug = None

            # self.latitude = self.client_json["Address"]["Coordinates"]["Latitude"]
            # self.longitude = self.client_json["Address"]["Coordinates"]["Longitude"]
            # self.has_feedback = self.client_json["occupancy"]["feedback"]
            # self.has_geofencing = self.client_json["occupancy"]["geofencing"]
            # self.has_scheduler = self.client_json["occupancy"]["scheduler"]
            # self.has_sensor = self.client_json["occupancy"]["sensor"]
            # self.has_smartplug = self.client_json["occupancy"]["smartplug"]
        except Exception as e:
            logging.exception(e)

    def get_feedback(self):
        """
        Gets user's feedback if any, else returns a number indicating there
        is any feedback
        :return float :  feedback
        """
        try:
            # if self.has_feedback:
            if self.feedback:
                feed_date = str_to_dt(self.feedback["timestamp"])
                if (self.date - feed_date) < delta(minutes=50):
                    feedback = int(self.feedback["presence"])
                    return feedback
            feedback = 0.0001
            return feedback
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyManager.get_feedback")
            return None

    def get_geofencing(self):
        """
        Gets user's geofencing if any, else returns a number indicating there
        is any geofencing
        :return float :  geofencing
        """
        try:
            # if self.has_geofencing:
            if self.geofencing:
                geof_date = str_to_dt(self.geofencing["timestamp"])
                if (self.date - geof_date) < delta(minutes=50):
                    geofencing = self.geofencing_home(self.latitude, self.longitude)
                    return int(geofencing)
            return 0.0001
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyManager.get_geofencing")
            return None

    def get_sensor(self):
        """
        :return: sensor
        """
        try:
            if self.sensor:
                sensor_date = str_to_dt(self.sensor["timestamp"])
                if (self.date - sensor_date) < delta(minutes=50):
                    sensor = int(self.sensor["presence"])
                    return sensor
            sensor = 0.0001
            return sensor
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyManager.get_sensor")
            return None

    def get_decision(self, filename, occupancy):
        """
        Decides user's occupancy based on the various inputs and a pretrained
        decision model
        :param filename filename: the filename of the decision model
        :param float occupancy: current occupancy
        :return int :  occupancy
        """
        try:
            decision_t = pd.DataFrame()
            decision_t['feedback'] = [self.get_feedback()]
            decision_t['geofencing'] = [self.get_geofencing()]
            decision_t['sensor'] = [self.get_sensor()]
            decision_t['device'] = [self.get_smartplug()]
            decision_t['sceduler'] = [self.get_scheduler()]
            decision_t['model'] = [occupancy]
            loaded_model = pickle.load(open(filename, 'rb'))
            decision_m = loaded_model.predict(decision_t)
            return int(decision_m[0])
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyManager.get_decision")
            return None

    def get_smartplug(self):
        """
        Gets user's state of devices(on/off) else returns a number indicating there
        is any indication of devices status
        :return float :  device state
        """
        try:
            if self.smartplug:
                smartplug_date = str_to_dt(self.smartplug["timestamp"])
                if (self.date - smartplug_date) < delta(minutes=50):
                    smartplug = int(self.smartplug["presence"])
                    return smartplug
            smartplug = 0.0001
            return smartplug
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyManager.get_device")
            return None

    def get_scheduler(self):
        """
        Get scheduler if client has one and check the occupancy for the current date
        :return: float occupancy
        """
        try:
            # if self.has_scheduler:
            if self.scheduler:
                presence = self.scheduler["presence"]
                scheduler_date = str_to_dt(self.scheduler["timestamp"])

                if (self.date - scheduler_date) < delta(minutes=50):
                    return presence
            return 0.0001
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyManager.get_sceduler")
            return None

    def geofencing_home(self, latitude_current, longitude_current):
        """
        Get geofencing if client has one and check the occupancy for the current date
        :return: float occupancy
        """
        if self.latitude and self.longitude:
            coords_1 = (self.latitude, self.longitude)
            coords_2 = (latitude_current, longitude_current)

            distance = round(geodesic(coords_1, coords_2).meters, 2)
            if distance <= 10:
                home = 1
                return home
            else:
                home = 0
                return home
        else:
            return 0.0001


def str_to_dt(st):
    """
    Converts a string object to datetime
    :param String st: date
    :return: datetime date
    """
    try:
        return dt.strptime(st, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Exception in Savings.str_to_dt")
        logging.exception(e)