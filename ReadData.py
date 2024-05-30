# -*- coding: utf-8 -*-
import configparser
import json
import os
from pathlib import Path
from datetime import datetime as dt, timedelta as delta
import logging


class ReadData:
    """
    Class containing all functions that
    get data from local files or the
    platform's api
    """
    def __init__(self, path):
        try:
            self.path = Path(path)
            self.files_path = self.path / "ClientFiles"
            self.general = self.path / "GeneralFiles"
            self.activity_path = self.path / "ActivityInference"
            self.comfort_path = self.path / "ComfortInference"
            self.disaggregation_path = self.path / "Disaggregation"
            self.occupancy_path = self.path / "OccupancyInference"
            self.recommendation_path = self.path / "Recommendation"

            self.conf = "Configs"
            self.js = "Json"
            self.models = "Models"
            self.other = "Other"
        except Exception as e:
            print("Exception in ReadData.__init__, ")
            logging.exception(e)

    def get_refrains(self):
        """
        :return: list containing the time steps for the recommendation refrain intervals
        """
        try:
            json_file = self.general / self.js / 'refrains.json'
            with open(json_file, encoding='utf-8') as f:
                data = json.load(f)
                return data["Time steps"]
        except Exception as e:
            print("Exception in ReadData.read_client_info, ")
            logging.exception(e)

    # def get_cwd(self):
    #     """
    #     :return: Current working directory
    #     """
    #     try:
    #         return self.path
    #     except Exception as e:
    #         print("Exception in ReadData.get_cwd, ")
    #         logging.exception(e)

    # def read_client_info(self, client):
    #     """
    #     :param String client: client name
    #     :return: loaded json file of this user
    #     """
    #     try:
    #         if client not in os.listdir(self.files_path):
    #             return -1
    #         jsonFile = self.files_path / client / self.js / 'Data.json'
    #         with open(jsonFile, encoding='utf-8') as f:
    #             data = json.load(f)
    #             return data
    #     except Exception as e:
    #         print("Exception in ReadData.read_client_info, ")
    #         logging.exception(e)

    def client_exists(self, client):
        if client not in os.listdir(self.files_path):
            return False
        else:
            return True

    def get_files(self, client, folder, room=None):
        """
        :param String client: client name
        :param String folder: tool name
        :param String room: room name
        :return: list of paths of the client's specific tool files
        """
        try:
            if client not in os.listdir(self.files_path):
                return -1
            path = self.files_path / client
            if room:
                path = path / room
            path = path / folder
            files = os.listdir(path)
            response = []
            for f in files:
                if 'keep' not in f:
                    tmp = path / f
                    response.append(str(tmp))
            return response
        except Exception as e:
            print("Exception in ReadData.get_files, ")
            logging.exception(e)

    def get_path_except_model_name(self, client):
        """
        :param String client: client name
        :return: path to the client's model folder
        """
        if client not in os.listdir(self.files_path):
            return -1
        return os.fsdecode(self.files_path / client / "Models")

    def get_general(self, folder, tool=None):
        """
        :param String folder: type of file
        :param String tool: tool name
        :return: list of paths for this tool and file type of the general files
        """
        try:
            path = self.general / folder
            if folder == "Models":
                path = path / tool
            files = os.listdir(path)
            response = []
            for f in files:
                tmp = path / f
                response.append(str(tmp))
            return path, response
        except Exception as e:
            print("Exception in ReadData.get_general, ")
            logging.exception(e)

    def get_duration(self, client, device):
        """
        :param String client: clients name
        :param String device: device name
        :return: duration from the clients config for this device
        """
        try:
            p = self.files_path / client / 'Configs' / 'config.ini'
            p = os.fsdecode(p)
            config = configparser.ConfigParser()
            config.optionxform=str
            config.read(p)
            if device not in dict(config.items("tempDuration")):
                print('den einai mes to dict')
                return None, p
            else:
                duration = int(config.get("tempDuration", device))
                return int(duration), p
        except Exception as e:
            logging.exception(e)
            print(f"In ReadData.get_duration, {client}")
            return None, None

    def get_occupancy_retrain_files(self, client):
        try:
            path = self.files_path / client
            path = path / "Models"

            response = {
                "DT": None,
                "HMM": None,
                "MANAGER": None,
                "path_to_models": path
            }
            models = self.get_files(client, "Models")
            if models == -1:
                return models
            for i in models:
                if 'DT.sav' == i:
                    response["DT"] = i
                if 'HMM.sav' == i:
                    response["HMM"] = i
                if 'MANAGER' in i:
                    response["MANAGER"] = i
            return response
        except Exception as e:
            print("Exception in ReadData.get_recommendation_files, ")
            logging.exception(e)

    def get_activity_retrain_files(self, client, device_name):
        try:
            path = self.files_path / client
            path = path / "Models"

            response = {
                "RF": None,
                "HMM": None,
                "path_to_models": path
            }
            models = self.get_files(client, "Models")
            if models == -1:
                return models
            for i in models:
                if device_name+'_RF.sav' == i:
                    response["RF"] = i
                if device_name+'_HMM.sav' == i:
                    response["HMM"] = i
            return response
        except Exception as e:
            print("Exception in ReadData.get_recommendation_files, ")
            logging.exception(e)

    def get_recommendation_files(self, client, room=1):
        """

        :param String client: client name
        :param int room: room number
        :return: model paths used by the recommendation class
        """
        try:
            path = self.files_path / client
            path = path / "Models"

            response = {
                "thermal_model_AC": None,
                "thermal_model_thermostat": None,
                "visualModel": None,
                "path_to_models": path
            }
            models = self.get_files(client, "Models")
            if models == -1:
                return models
            for i in models:
                if 'hvac' in i and str(room) in i:
                    response["thermal_model_AC"] = i
                if 'thermostat' in i and str(room) in i:
                    response["thermal_model_thermostat"] = i
                if 'visual' in i and str(room) in i:
                    response["visualModel"] = i
            return response
        except Exception as e:
            print("Exception in ReadData.get_recommendation_files, ")
            logging.exception(e)

    def get_path_recommendation(self):
        return self.recommendation_path

    def get_path_activity(self):
        return self.activity_path

    def get_path_comfort(self):
        return self.comfort_path

    def get_path_disaggregation(self):
        return self.disaggregation_path

    def get_path_occupancy(self):
        return self.occupancy_path

    # def get_path_data(self):
    #     return self.data_path
