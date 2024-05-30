from Comfort.VisualComfort import VisualComfort
from Comfort.ThermalComfort import ThermalComfort
import json
import logging


class ComfortInference:
    """The main class of the Comfort Inference. It is the entry point that 
    executes the Comfort estimation when called to estimate thermal comfort 
    and visual comfort.
    """

    def __init__(self, config_file):
        """The constructor of the Comfort Inference class.
        :param config_file: path to the config file
        """
        try:
            self.config_file = config_file
        except Exception as e:
            logging.exception(e)
            print(e, "In ComfortInference.__init__")

    def get_thermal_comfort(self, data):
        """Gets all the data from the constructor parameters and calls all the
        functions needed to estimate thermal and visual comfort.
        :return string : The comfort estimation results. As formatted from the 
        FormatResponse function.
        """
        try:
            response = None
            if data["temperature"] is not None and data["humidity"] is not None:
                temperature = float(data["temperature"])
                humidity = float(data["humidity"])
                timestamp = data["timestamp"]
                th = ThermalComfort(self.config_file)
                response = round(float(th.thermal_estimation_adjust(temperature, humidity, timestamp)), 3)
                # PMV_ASHRAE = th.thermal_estimation_ashrae(temperature, humidity, file, timestamp)
                # response = {'thermal_comfort': str(round(PMV_adjust, 3)), 'thermal_ashrae': round(PMV_ASHRAE, 3), 'visual_comfort': round(VC, 3)}
            return response
        except Exception as e:
            logging.exception(e)
            print(e, "In ComfortInference.get_comfort")
            return None

    def get_visual_comfort(self, data):
        """Gets all the data from the constructor parameters and calls all the
         functions needed to estimate thermal and visual comfort.
        :return string : The comfort estimation results. As formatted from the
        FormatResponse function.
        """
        try:
            response = None
            if data["luminance"] is not None and data["latitude"] is not None and data["longitude"] is not None:
                lux = int(data["luminance"])
                latitude = data["latitude"]
                longitude = data["longitude"]
                timestamp = data["timestamp"]
                v = VisualComfort(self.config_file)
                response = round(float(v.visual_calculation(lux, latitude, longitude, timestamp)), 3)
            return response
        except Exception as e:
            logging.exception(e)
            print(e, "In ComfortInference.get_comfort")
            return None
