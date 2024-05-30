import errno
# import faulthandler
import json
import logging
import os
import shutil
import warnings
from datetime import datetime as dt, timedelta as delta
from pathlib import Path
import numpy as np

import joblib

from Activity.ActivityModels import ActivityModels
from Comfort.ComfortInference import ComfortInference
from Disaggregation.Disaggregate import Disaggregate
from Occupancy.OccupancyInference import OccupancyInference
from ReadConfig import ReadConfig
from ReadData import ReadData
from Recommendation.Recommend import Recommend
from Recommendation.Savings import Savings
from Recommendation.ThermalComfortHvac import ThermalComfortHvac
from Recommendation.ThermalComfortThermostat import ThermalComfortThermostat
from Recommendation.VisualComfortLights import VisualComfortLights
from Occupancy.OccupancyModels import OccupancyModels

import random

warnings.filterwarnings("ignore")


class Tools:
    def __init__(self):
        # faulthandler.enable()
        # atexit.register(exit_handler)
        self.conf = ReadConfig()
        # localTimeZone = pytz.timezone(conf.timeZone)
        self.read_data = ReadData(self.conf.path)
        self.path_to_models, self.disaggregation_models = self.read_data.get_general("Models", "Disaggregation")
        self.path_to_config, self.general_config_file = self.read_data.get_general("Configs")
        self.models = {}
        self.disaggregation = Disaggregate(self.models, self.general_config_file)
        # Create model dictionary suitable for the respected OS
        if os.name == "posix":
            for i in self.disaggregation_models:
                one = i.split("/")[-1]
                if "keep" not in one:
                    one = one[:-4]
                    self.models[one] = joblib.load(Path(i))
        else:
            for i in self.disaggregation_models:
                one = i.split("\\")[-1]
                if "keep" not in one:
                    one = one[:-4]
                    self.models[one] = joblib.load(Path(i))

    def disaggregate(self, args):
        """
        Runs the disaggregation tool for this client
        Returns the predicted disaggregation, if any is produced.
        :return: disaggregation output

        Example of Input
        args = {
            "devices": [
                "fridge",
                "oven",
                "water_heater",
                "AC",
                "iron",
                "toaster"
            ],
            "consumption_list": [
                ["2020-03-01 19:14:00", 2024.0, 294.0],
                ["2020-03-01 19:15:00", 2024.0, 294.0],
                ["2020-03-01 19:16:00", 2024.0, 294.0],
                ["2020-03-01 19:17:00", 2024.0, 294.0],
                ["2020-03-01 19:18:00", 2024.0, 294.0]
            ]
        }
        """
        try:
            result = self.disaggregation.run(args)
            if result:
                result["timestamp"] = dt_to_str(dt.utcnow())
                return result
            else:
                return {}
        except Exception as e:
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.disaggregate"
                }
            }

    def comfort(self, args):
        """
        Runs the comfort tool for this client
        Returns the predicted comfort
        :return: Comfort output

        Example of Input
        args = {
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
        """
        try:
            lat, log = None, None
            client = args["client"]
            if not self.read_data.client_exists(client):
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            timestamp = str_to_dt(args["timestamp"])
            if "latitude" in args.keys():
                lat = args["latitude"]
            if "longitude" in args.keys():
                log = args["longitude"]
            path_to_config, config_file = self.read_data.get_general("Configs")
            devices = args["devices"]
            comforts = {}
            cf = ComfortInference(config_file)
            for device in devices.keys():
                tem, hum, lum, pmv, vcm = None, None, None, None, None
                if "temperature" in devices[device].keys():
                    tem = devices[device]["temperature"]
                if "humidity" in devices[device].keys():
                    hum = devices[device]["humidity"]
                if not (tem is None and hum is None and timestamp is None):
                    thermal_input = {
                        "humidity": hum,
                        "temperature": tem,
                        "timestamp": timestamp
                    }
                    pmv = cf.get_thermal_comfort(thermal_input)

                if "luminance" in devices[device].keys():
                    lum = devices[device]["luminance"]
                if not (lum is None and lat is None and log is None and timestamp is None):
                    visual_input = {
                        "luminance": lum,
                        "latitude": lat,
                        "longitude": log,
                        "timestamp": timestamp
                    }
                    vcm = cf.get_visual_comfort(visual_input)
                comforts[device] = {
                    "thermal_comfort": pmv,
                    "visual_comfort": vcm
                }
            if comforts is not {} and comforts:
                comforts["timestamp"] = dt_to_str(dt.utcnow())
            return comforts
        except Exception as e:
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.comfort"
                }
            }

    def occupancy(self, args):
        """
            Runs the occupancy tool for this client,
            Returns the output predicted occupancy.
            :return: Occupancy output

            Example of Input
            args = {
                "client": "",
                "timestamp": "",
                "consumption": "",
                "manager_data" = {
                    "feedback": "",
                    "geofencing": "",
                    "scheduler": "",
                    "sensor": "",
                    "smartplug": ""
                },
                "reinit": ""
            }
        """
        try:
            client = args["client"]
            unused, config_file = self.read_data.get_general("Configs")
            savs = self.read_data.get_files(client, "Models")
            
            if savs == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }

            dtc, hmm, mana = "", "", ""
            for i in savs:
                if os.name == "posix":
                    pth = i.split("/")[-1]
                else:
                    pth = i.split("\\")[-1]
                if pth == "DT.sav":
                    dtc = i
                if pth == "HMM.sav":
                    hmm = i
                if pth == "MANAGER.sav":
                    mana = i

            args["files"] = {
                "DT": dtc,
                "HMM": hmm,
                "MANAGER": mana
            }

            oc = OccupancyInference(args=args,
                                    config_file=config_file,
                                    read_data=self.read_data,
                                    reinit_occupancy_configs=False)
            occupancy_output = oc.get_occupancy()
            if occupancy_output == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            if occupancy_output is not {} and occupancy_output:
                occupancy_output["timestamp"] = dt_to_str(dt.utcnow())
            return occupancy_output
        except Exception as e:
            print(" in run_occupancy")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.occupancy"
                }
            }

    # TODO vale pio eksw to REINIT
    def activity(self, args):
        """
            Runs the activity tool for this client
            and returns the activity tool output, if any is produced.
            :return: Activity output, if any is produced

            Example of Input
            args = {
                "client": "00606EFFFEABADEF",
                "timestamp": "2020-03-01 19:18:00",
                "devices": {
                    "fridge": "82.12",
                    "oven": "0.0",
                    "water_heater": "0.0",
                    "AC": "836.41",
                    "toaster": "2017.96"
                },
                "occupancy": {
                    "occupancy": 2.0
                }
            }
        """
        try:
            client = args["client"]
            timestamp = str_to_dt(args["timestamp"])
            dis_out = args["devices"]
            occ_out = args["occupancy"]
            reinit = False
            output = {}
            if dis_out and occ_out:
                activities = {}
                path_to_config, config_file = self.read_data.get_general("Configs")
                savs = self.read_data.get_files(client, "Models")
                if savs == -1:
                    return {
                        "timestamp": dt_to_str(dt.utcnow()),
                        "error": "client does not exist in filesystem"
                    }
                path_except_model_name = self.read_data.get_path_except_model_name(client)
                client = args["client"]
                for key in dis_out.keys():
                    activity_output = None
                    duration, act_conf = self.read_data.get_duration(client, key)
                    if act_conf and (duration is not None):
                        try:
                            if occ_out["occupancy"] != 2:
                                activity_output = {"activity": 0}
                            else:
                                rf, hmm = "", ""
                                for i in savs:
                                    if key + "_RF" in i:
                                        rf = i
                                    if key + "_HMM" in i:
                                        hmm = i
                                files = {
                                    "RF": rf,
                                    "HMM": hmm,
                                    "path": path_except_model_name
                                }
                                if rf and hmm:
                                    activity_input = {
                                        "client": client,
                                        # "devices": self.read_data.read_client_info(client)["devices"],
                                        "reinit": reinit,
                                        "duration": duration,
                                        "timestamp": timestamp,
                                        "activity_config": act_conf,
                                        "general_config": config_file,
                                        "device_name": key
                                    }
                                    ac = ActivityModels(args=activity_input, files=files)
                                    activity_output = ac.get_activity(float(dis_out[key]))
                            if activity_output:
                                output = {
                                    "device": key,
                                    "activity": activity_output["activity"]
                                    # device_name: activity_output
                                }
                        except Exception as e:
                            logging.exception(e)
                            print("in run_activity")
                    if output:                       
                        activities[output["device"]] = output["activity"]
                if activities is not {} and activities:
                    activities["timestamp"] = dt_to_str(dt.utcnow())
                return activities
            else:
                return None
        except Exception as e:
            print(" in run_activity")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.activity"
                }
            }

    def recommendation(self, args):
        """
            Runs the recommendation tool for one client, using
            all the available data.
            Returns the recommendations, if any are produced.

            args = {
                "timestamp": "2020-03-01 19:18:00",
                "client": "00606EFFFEAB11DB",
                "reinitialize_recommendations": false,
                "devices": {
                    "fridge": 82.12,
                    "oven": 0.0,
                    "water_heater": 0.0,
                    "AC": 836.41,
                    "toaster": 2017.96
                },
                "night_power_discount": false,
                "co2_threshold": 200,
                "humidity_threshold": 10,
                "comfort": {
                    "hvac": {
                        "thermal_comfort": 1.266,
                        "visual_comfort": 1.424
                    },
                    "thermostat": {
                        "thermal_comfort": 1.919,
                        "visual_comfort": -1.144
                    },
                    "sensor": {
                        "thermal_comfort": null,
                        "visual_comfort": -1.144
                    }
                },
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
                "weather":
                    {
                        "temperature": 25.00,
                        "humidity": 40.00,
                        "ghi": 600
                    },
                "indoorConditions":
                    {
                        "temperature": 21.00,
                        "humidity": 60.00,
                        "luminance": 800,
                        "co2": 150
                    },
                "hvac":
                    {
                        "set_temp": 26.00,
                        "status": 1
                    },
                "lighting":
                    {
                        "dimmer": 80,
                        "status": 1
                    },
                "thermostat":
                    {
                        "set_temp": 26.00,
                        "status": 1
                    },
                "generic_upper_hvac": false,
                "generic_lower_hvac": false,
                "generic_upper_thermostat": false,
                "generic_lower_thermostat": false,
                "generic_turn_off_standby": false,
                "generic_open_windows": false,
                "generic_change_setpoint": false,
                "generic_efficient_heating": false,
                "aggregate_savings": [],
                "weekly_smartplugs": [],
                "weekly_consumption": []
            }
        """
        try:
            client = args["client"]
            if not self.read_data.client_exists(client):
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            timestamp = str_to_dt(args["timestamp"])
            args["files"] = self.read_data.get_recommendation_files(client)
            args["train"] = False
            args["water_heater_threshold"] = self.conf.water_heater_threshold
            # TODO push outwards

            if "reinitialize_recommendations" not in args:
                args["reinitialize_recommendations"] = False
            rec = Recommend(args, read_data=self.read_data)
            response = rec.get_recommendation()
            ret = {}
            if response is not {} and response:
                ret = {
                    "timestamp":  dt_to_str(dt.utcnow()),
                    "recommendations": response,
                }
            return ret
        except Exception as e:
            logging.exception(e)
            print("in run_recommendation")
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.recommendation"
                }
            }

    def occupancy_retrain(self, args):
        """
        Retrain Occupancy
        Example Body: {
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
        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": true
        }
        """
        try:
            client = args["client"]
            unused, config_file = self.read_data.get_general("Configs")
            args["config_file"] = config_file[0]
            files = self.read_data.get_occupancy_retrain_files(client)
            if files == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }

            if files["DT"]:
                dt_sav = files["DT"]
            else:
                dt_sav = files["path_to_models"] / "DT.sav"
            if files["HMM"]:
                hmm_sav = files["HMM"]
            else:
                hmm_sav = files["path_to_models"] / "HMM.sav"
            savs = {
                "DT": dt_sav,
                "HMM": hmm_sav
            }

            mdtc = OccupancyModels(args=args, files=savs, train=True)
            _dt, _hmm = mdtc.train()

            if _dt and _hmm:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": True
                }
            else:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": False
                }
        except Exception as e:
            logging.exception(e)
            print("in occupancy_retrain")
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.occupancy_retrain"
                }
            }

    def occupancy_correction(self, args):
        """
        Correct Already Calculated Occupancy Values
        Example Body: {
            "client": "00606EFFFEABADEF",
            "timestamp": "2021-10-19 08:59:41",
            "occupancy": [
                    ["2021-10-19 08:59:00", 0],
                    ["2021-10-19 09:00:00", 1],

                    ["2021-10-19 10:50:00", 2]
                ]
        }

        response: {
            "client": "00606EFFFEABADEF",
            "timestamp": "2021-10-19 09:00:00",
            "occupancy": [
                    ["2021-10-19 08:59:00", 2],
                    ["2021-10-19 09:00:00", 2],

                    ["2021-10-19 10:50:00", 2]
                ]
        }
        """
        occupancy = args["occupancy"]
        try:
            occupancy, msg = median(occupancy, 40)
            args["occupancy"] = occupancy
            args["timestamp"] = dt_to_str(dt.utcnow())
            return args
        except Exception as e:
            print(e, " in occupancy_correction, correct values")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.occupancy_correction"
                }
            }

    def activity_retrain(self, args):
        """
        Retrain Activity
        Example Body: {
            "client": "00606EFFFEABADEF",
            "training_set": {
                "device_name": "fridge",
                "device_power": [
                    ["2021-10-19 08:59:00", 700.0],
                    ["2021-10-19 09:00:00", 750.0],

                    ["2021-10-19 10:50:00", 800.0]
                ]
            }
        }

        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": true
        }

        """
        try:
            client = args["client"]
            unused, config_file = self.read_data.get_general("Configs")
            args["general_config"] = config_file[0]
            device_name = args["training_set"]["device_name"]
            duration, act_conf = self.read_data.get_duration(client, device_name)
            if duration is None:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "device does not exist in filesystem"
                }

            args["activity_config"] = act_conf
            files = self.read_data.get_activity_retrain_files(client=client, device_name=device_name)
            if files == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }

            if files["RF"]:
                rf_sav = files["RF"]
            else:
                filename = device_name + "_RF.sav"
                rf_sav = files["path_to_models"] / filename
            if files["HMM"]:
                hmm_sav = files["HMM"]
            else:
                filename = device_name + "_HMM.sav"
                hmm_sav = files["path_to_models"] / filename
            savs = {
                "RF": rf_sav,
                "HMM": hmm_sav
            }
            ac = ActivityModels(args=args, files=savs, train=True)
            models, msg = ac.train()

            if models[0] and models[1]:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": True
                }
            else:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": False,
                    "message": msg
                }
        except Exception as e:
            logging.exception(e)
            print("in activity_retrain")
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.activity_retrain"
                }
            }

    def activity_correction(self, args):
        """
        Correct Already Calculated Activity Values
        Example Body: {
            "client": "00606EFFFEABADEF",
            "devices": {
                "fridge": {
                    "activity": [
                        ["2021-10-19 08:59:00", 0],
                        ["2021-10-19 09:00:00", 1],

                        ["2021-10-19 10:50:00", 1]
                    ]
                },

                "oven": {
                    "activity": [
                        ["2021-10-19 08:59:00", 1],
                        ["2021-10-19 09:00:00", 1],

                        ["2021-10-19 10:50:00", 1]
                    ]
                }
            }
        }

        response: {
            "client": "00606EFFFEABADEF",
            "timestamp": "2021-10-19 08:50:40",
            "devices": {
                "fridge": {
                    "activity": [
                        ["2021-10-19 08:59:00", 0],
                        ["2021-10-19 09:00:00", 0],

                        ["2021-10-19 10:50:00", 0]
                    ]
                },

                "oven": {
                    "activity": [
                        ["2021-10-19 08:59:00", 0],
                        ["2021-10-19 09:00:00", 0],

                        ["2021-10-19 10:50:00", 0]
                    ]
                }
            }
        }
        """
        try:
            devices = args["devices"]
            for device in devices.keys():
                dev_activity = devices[device]["activity"]
                dev_activity, msg = median(dev_activity, 6)
                if msg != 200:
                    args["devices"][device]["activity"] = None
                    args["devices"][device]["error"] = msg
                else:
                    args["devices"][device]["activity"] = dev_activity
            args["timestamp"] = dt_to_str(dt.utcnow())
            return args
        except Exception as e:
            print(e, " in activity_correction")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.activity_correction"
                }
            }

    def vcl_train(self, args):
        """
        Visual Comfort Lights Module Train
        Example Body: {
            "client": "00606EFFFEABADEF",
            "training_set": [
                ["2021-10-19 08:59:00", 700.0, 100.0, 1.322],
                ["2021-10-19 09:00:00", 750.0, 100.0, 1.324],

                ["2021-10-19 10:50:00", 800.0, 100.0, 1.400]
            ]
        }

        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": true,
            "score": 71.14
        }
        """
        try:
            files = self.read_data.get_recommendation_files(args["client"])
            if files == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            if files["visualModel"]:
                sav = files["visualModel"]
            else:
                sav = files["path_to_models"] / "visual_1.sav"
            vcl = VisualComfortLights(args=args, sav=sav, train=True)
            model, score = vcl.train()
            if model:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": True,
                    "score": round(score, 2)
                }
            else:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": False
                }
        except Exception as e:
            print(e, " in vcl_train")
            logging.exception(e)
            return {
                "error_message": {
                    "msg": e,
                    "def": "Tools.vcl_train"
                }
            }

    def tct_train(self, args):
        """
        Thermal Comfort Thermostat Train
        Example Body: {
            "client": "00606EFFFEABADEF",
            "training_set": [
                ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 23.0, 1],
                ["2021-10-19 09:10:00", 23.5, 40.0, 30.1, 60.3, 23.0, 1],

                ["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 23.0, 1]
            ]
        }

        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": true,
            "score": 71.14
        }
        """
        try:
            files = self.read_data.get_recommendation_files(args["client"])
            if files == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            if files["thermal_model_thermostat"]:
                sav = files["thermal_model_thermostat"]
            else:
                sav = files["path_to_models"] / "thermal_thermostat_1.sav"
            tct = ThermalComfortThermostat(args=args, sav=sav, train=True)
            model, score = tct.train()
            if model:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": True,
                    "score": round(score, 2)
                }
            else:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": False
                }
        except Exception as e:
            print(e, " in tct_train")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.tct_train"
                }
            }

    def tch_train(self, args):
        """
        Thermal Comfort HVAC Train
        Example Body: {
            "client": "00606EFFFEABADEF",
            "training_set": [
                ["2021-10-19 08:59:00", 23.5, 40.0, 30.1, 60.3, 25.0, 23.0, 1],
                ["2021-10-19 09:00:00", 23.5, 40.0, 30.1, 60.3, 25.0, 23.0, 1],

                ["2021-10-19 10:00:00", 23.5, 40.0, 30.1, 60.3, 25.0, 23.0, 1]
            ]
        }

        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": true,
            "score": 71.14
        }
        """
        try:
            files = self.read_data.get_recommendation_files(args["client"])
            if files == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            if files["thermal_model_AC"]:
                sav = files["thermal_model_AC"]
            else:
                sav = files["path_to_models"] / "thermal_hvac_1.sav"
            tch = ThermalComfortHvac(args=args, sav=sav, train=True)
            model, score = tch.train()
            if model:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": True,
                    "score": round(score, 2)
                }
            else:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": False
                }
        except Exception as e:
            print(e, " in tch_train")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.tch_train"
                }
            }

    def new_client(self, args):
        """
        Create Client in Filesystem

        Example Body: {
            "client": "00606EFFFEABADEF"
        }
        response: {
            "timestamp": "2021-10-19 08:50:40",
            "client_created": true,
            "message": ""
        }
        """
        response = {
            "timestamp": dt_to_str(dt.utcnow()),
            "client_created": False,
            "message": ""
        }
        try:
            clients_path = Path('ClientFiles')
            dst = clients_path / args["client"]
            if not os.path.isdir(dst):
                src = clients_path / "EXAMPLE"
                try:
                    shutil.copytree(src, dst)
                    response["client_created"] = True
                    response["message"] = "client created"
                    return response
                except OSError as exc:
                    if exc.errno == errno.ENOTDIR:
                        shutil.copy(src, dst)
                        response["client_created"] = True
                        response["message"] = "client created"
                        return response
                    else:
                        response["message"] = str(exc)
                        return response
            else:
                response["message"] = "Client already exists in Filesystem"
                return response
        except Exception as e:
            response["error"] = {
                    "msg": e,
                    "def": "Tools.tch_train"
                }
            return response

    def create_occupancy_models(self, args):
        """
        Create Occupancy Models
        Example Body: {
            "client": "00606EFFFEABADEF",
            "mains_power": [
                ["2021-10-19 08:59:00", 700.0],
                ["2021-10-19 09:00:00", 750.0],

                ["2021-10-19 10:50:00", 800.0]
            ]
        }

        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": true
        }
        """
        try:
            client = args["client"]
            unused, config_file = self.read_data.get_general("Configs")
            args["config_file"] = config_file[0]
            files = self.read_data.get_occupancy_retrain_files(client)
            if files == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }

            if files["DT"]:
                dt_sav = files["DT"]
            else:
                dt_sav = files["path_to_models"] / "DT.sav"
            if files["HMM"]:
                hmm_sav = files["HMM"]
            else:
                hmm_sav = files["path_to_models"] / "HMM.sav"
            savs = {
                "DT": dt_sav,
                "HMM": hmm_sav
            }
            mdtc = OccupancyModels(args=args, files=savs, train=True)
            _dt, _hmm = mdtc.create_models()

            if _dt and _hmm:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": True
                }
            else:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "train_success": False
                }
        except Exception as e:
            print(e, " in tch_train")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.create_occupancy_models"
                }
            }

    def create_activity_models(self, args):
        """
        Create Device Profile Models
        Example Body: {
            "client": "00606EFFFEABADEF",
            "training_set": {
                "fridge": {
                    [
                        ["2021-10-19 08:59:00", 700.0],
                        ["2021-10-19 09:00:00", 750.0],

                        ["2021-10-19 10:50:00", 800.0]
                    ]
                },

                "oven": {
                    [
                        ["2021-10-19 08:59:00", 700.0],
                        ["2021-10-19 09:00:00", 750.0],

                        ["2021-10-19 10:50:00", 800.0]
                    ]
                }
            }
        }

        response: {
            "timestamp": "2021-10-19 08:50:40",
            "train_success": {
                "fridge": true,

                "oven": true
            }
        }
        """
        try:
            response = {
                "train_success": {
                }
            }
            client = args["client"]
            fls = self.read_data.get_files(client=client, folder="Models")
            if fls == -1:
                return {
                    "timestamp": dt_to_str(dt.utcnow()),
                    "error": "client does not exist in filesystem"
                }
            unused, config_file = self.read_data.get_general("Configs")
            args["general_config"] = config_file[0]
            for key in args["training_set"].keys():

                new_args = {
                    "client": client,
                    "training_set": {
                        "device_name": key,
                        "device_power": args["training_set"][key]
                    }
                }
                duration, act_conf = self.read_data.get_duration(client, key)

                new_args["activity_config"] = act_conf
                new_args["general_config"] = args["general_config"]
                files = self.read_data.get_activity_retrain_files(client=client, device_name=key)
                if files == -1:
                    return {
                        "timestamp": dt_to_str(dt.utcnow()),
                        "error": "client does not exist in filesystem"
                    }

                if files["RF"]:
                    rf_sav = files["RF"]
                else:
                    filename = key + "_RF.sav"
                    rf_sav = files["path_to_models"] / filename
                if files["HMM"]:
                    hmm_sav = files["HMM"]
                else:
                    filename = key + "_HMM.sav"
                    hmm_sav = files["path_to_models"] / filename
                savs = {
                    "RF": rf_sav,
                    "HMM": hmm_sav
                }
                ac = ActivityModels(args=new_args, files=savs, train=True)
                _rf, _hmm = ac.create_models()
                if _rf is None or _hmm is None:
                    response["train_success"][key] = False
                else:
                    response["train_success"][key] = True
            response["timestamp"] = dt_to_str(dt.utcnow())
            return response
        except Exception as e:
            print(e, " in tch_train")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.create_activity_models"
                }
            }

    def delete_client(self, args):
        """
        Delete Client in Filesystem

        Example Body: {
            "client": "00606EFFFEABADEF"
        }
        response: {
            "timestamp": "2021-10-19 08:50:40",
            "client_deleted": true,
            "message": "Client deleted from filesystem"
        }
        """
        response = {
            "timestamp": dt_to_str(dt.utcnow()),
            "client_deleted": False,
            "message": ""
        }
        try:
            clients_path = Path('ClientFiles')
            dst = clients_path / args["client"]
            if os.path.isdir(dst):
                try:
                    shutil.rmtree(dst)
                    response["client_deleted"] = True
                    response["message"] = "Client deleted from filesystem"
                    return response
                except Exception as e:
                    response["message"] = "Unknown Exception: " + str(e)
                    return response
            else:
                response["message"] = "Client was not found in filesystem"
                return response
        except Exception as e:
            response["error"] = {
                    "msg": e,
                    "def": "Tools.create_activity_models"
                }
            return response

    def savings(self, args):
        """
        Get Savings for recommendation
        Example Body: {
            "timestamp": "2020-03-01 17:10:00",
            "client": "00606EFFFEAB11DB",
            "number": 6,
            "sent_at": "2020-03-01 16:10:00",
            "power_interval": 1,
            "power_after_recommendation": [
                ["2020-01-01 00:00:00", 700.0],
                ["2020-01-01 00:01:00", 637.0],
                ["2020-01-01 00:02:00", 749.0],
                ["2020-01-01 00:03:00", 717.0],
                ["2020-01-01 00:04:00", 787.0],
                ["2020-01-01 00:05:00", 741.0],

                ["2020-01-01 00:59:00", 643.0],
                ["2020-01-01 01:00:00", 628.0]
            ]
        }
        response: {
          "number": 6,
          "sent_at": "2020-03-01 16:10:00",
          "timestamp": "2020-03-01 17:10:00",
          "type": "passive",
          "savings": 1000.0
        }
        """
        try:
            clients_path = Path('ClientFiles')
            dst = clients_path / args["client"]
            if os.path.isdir(dst):
                savings = Savings(args=args)
                response = savings.get_savings()
                response["timestamp"] = dt_to_str(dt.utcnow())
                return response
            else:
                return {
                    "message": "Client was not found in filesystem",
                    "timestamp": dt_to_str(dt.utcnow())
                }

        except Exception as e:
            print(e, " in savings")
            logging.exception(e)
            return {
                "error": {
                    "msg": e,
                    "def": "Tools.savings"
                }
            }

    # def inference_test(self, args):
    #     # tch
    #     files = self.read_data.get_recommendation_files(args["client"])
    #     if files == -1:
    #         return {
    #             "timestamp": dt_to_str(dt.utcnow()),
    #             "error": "client does not exist in filesystem"
    #         }
    #     if files["thermal_model_hvac"]:
    #         sav = files["thermal_model_hvac"]
    #     else:
    #         sav = files["path_to_models"] / "thermal_hvac_1.sav"
    #         print(sav)
    #     tch = ThermalComfortHvac(args=args, sav=sav, train=False)
    #     heat, cool, mode = tch.predict({
    #         "temperature": 23.5,
    #         "humidity": 40.0,
    #         "temperature_out": 16.0,
    #         "humidity_out": 70.0,
    #         "date": dt.utcnow()
    #     })
    #     print(f"heat: {heat}, cool: {cool}, mode: {mode}")
    #
    #     # tct
    #     if files["thermal_model_thermostat"]:
    #         sav = files["thermal_model_thermostat"]
    #     else:
    #         sav = files["path_to_models"] / "thermal_thermostat_1.sav"
    #     tct = ThermalComfortThermostat(args=args, sav=sav, train=False)
    #     set_temp, mode = tct.predict({
    #         "temperature": 23.5,
    #         "humidity": 40.0,
    #         "temperature_out": 16.0,
    #         "humidity_out": 70.0,
    #         "date": dt.utcnow()
    #     })
    #     print(f"set_temp: {set_temp}, mode: {mode}")
    #
    #     # vcl
    #     if files["visual_model"]:
    #         sav = files["visual_model"]
    #     else:
    #         sav = files["path_to_models"] / "visual_1.sav"
    #     vcl = VisualComfortLights(args=args, sav=sav, train=False)
    #     dimmer, mode = vcl.predict({
    #         "luminance": 1000,
    #         "ghi": 800,
    #         "visual_comfort": 1.22,
    #         "date": dt.utcnow()
    #     })
    #     print(f"dimmer: {dimmer}, mode: {mode}")


def median(measurement, window):
    """
    Corrects a sequence of values with the use of a median filter
    :param measurement: the list that will be corrected
    :param int window: The size of the sliding window
    :return list: corrected sequence
    """
    try:
        temp = measurement
        sequence, times = [], []
        for o in measurement:
            sequence.append(o[1])
        size = len(sequence)
        if size > (window * 2):
            middle_index = int((window - 1) / 2)
            for i in range(size):
                sort = []
                if i < (size - (window - 1)):
                    for a in range(window):
                        sort.append(sequence[i + a])
                    correction = int(np.median(sort))
                    position = i + middle_index
                    sequence[position] = correction
            for o in range(len(sequence)):
                temp[o][1] = sequence[o]
            return temp, 200
        else:
            return None, "Too small measurement interval"
    except Exception as e:
        logging.exception(e)
        print(e, "In Tools.median")
        return None, str(e)


def str_to_dt(st):
    """
    Converts a string object to datetime
    :param String st: date
    :return: datetime date
    """
    try:
        return dt.strptime(st, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Exception in Tools.str_to_dt")
        logging.exception(e)


def dt_to_str(dat):
    try:
        return dat.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Exception in Tools.dt_to_str")
        logging.exception(e)
        return None


def create_input_savings():
    date = dt(2022, 2, 3, 10, 0, 0)
    print(dt_to_str(date))
    my_input = {
        "power_after_recommendation": [
            [dt_to_str(date), 750.0],
        ],
    }
    for minute in range(160):
        date += delta(minutes=1)
        my_input["power_after_recommendation"].append([dt_to_str(date), round(700.0 + (random.randrange(-1000, 1000, 10) / 10), 2)])

    for i in range(15, 50, 1):
        my_input["power_after_recommendation"][i][1] = 0
    print(json.dumps(my_input))


def create_input_water_heater():
    date = dt(2022, 2, 3, 10, 0, 0)
    print(dt_to_str(date))
    my_input = {
        "water_heater": [
            [dt_to_str(date), 500.0],
        ],
    }
    for minute in range(59):
        date += delta(minutes=1)
        my_input["water_heater"].append([dt_to_str(date), round(500.0 + (random.randrange(-1000, 1000, 10) / 10), 2)])

    # for i in range(50, 100, 1):
    #     my_input["power"][i][1] = 20.5
    print(json.dumps(my_input))


if __name__ == "__main__":
    print("Do not call as main")
    create_input_water_heater()
