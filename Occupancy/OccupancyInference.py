from Occupancy.OccupancyManager import OccupancyManager
from Occupancy.OccupancyModels import OccupancyModels
import configparser
import datetime
from datetime import timedelta as delta
import logging
from datetime import datetime as dt


class OccupancyInference:
    """The main class of the Occupancy Inference. It is the entry point that 
    executes the Occupancy inference when called to estimate current occupancy.
    """

    def __init__(self, args, config_file, read_data, reinit_occupancy_configs=None):
        try:
            self.data = args
            self.config_file = config_file
            self.date = str_to_dt(args["timestamp"])
            self.manager_data = self.data["manager_data"]
            self.read_data = read_data
            self.client = self.data["client"]
            self.config_path = self.read_data.get_files(self.client, "Configs")[0]
            self.config = configparser.ConfigParser()
            self.config.read(self.config_path)
            if reinit_occupancy_configs:
                self.reinit_config()
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyInference.__init__")

    def reinit_config(self):
        self.config.set("Occupancy", "last_train", "2020-03-10T00:00:00.000Z")
        self.config.write(open(self.config_path, "w"))

    def weekends(self, date):
        weekends = []
        for d in date:
            if d < 5:
                weekends.append(0)
            else:
                weekends.append(1)
        return weekends

    def format_response(self, occupancy):
        """Formats the estimated Occupancy as a string.
        :param int occupancy: current occupancy
        :return string : The format of the string is:
            string={'occupancy':occupancy}
        """
        try:
            string = {'occupancy': float(occupancy)}
            return string
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyInference.format_response")

    def get_occupancy(self):
        """Gets all the data from the constructor parameters and calls all the 
         functions needed to estimate Occupancy.
        :return string : The occupancy estimation results. As formatted from the 
        FormatResponse function.
        """
        try:
            file_dm = self.data["files"]["MANAGER"]
            timestamp = str_to_dt(self.data["timestamp"])
            args = {
                "client": self.client,
                "config_file": self.config_file
            }
            oc = OccupancyModels(args=args, files=self.data["files"])
            occupancy = oc.predict_occupancy(consumption=self.data["consumption"], timestamp=timestamp)

            dec_oc = OccupancyManager(self.manager_data, self.date)
            if occupancy == 0 or occupancy == 1 or occupancy == 2:
                oc = dec_oc.get_decision(file_dm, occupancy)
                if 9 < self.date.hour <= 23 and oc == 1:
                    oc = 0
                if 0 <= self.date.hour <= 9 and oc == 0:
                    oc = 1
            else:
                oc = dec_oc.get_decision(file_dm, 0.0001)
            response = self.format_response(oc)
            return response
        except Exception as e:
            logging.exception(e)
            print(e, "In OccupancyInference.get_occupancy")
            return None


def str_to_dt(st):
    """
    Convert a String object to datetime
    :param st: String timestamp object
    :return: Datetime timestamp object
    """
    try:
        return dt.strptime(st, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Exception in HandleClientConfig.str_to_dt, ")
        logging.exception(e)
        return None


def dt_to_str(dat):
    """
    Convert a Datetime object to String
    :param dat: Datetime timestamp object
    :return: String timestamp object
    """
    try:
        return dat.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception as e:
        print("Exception in HandleClientConfig.dt_to_str")
        logging.exception(e)
        return None
