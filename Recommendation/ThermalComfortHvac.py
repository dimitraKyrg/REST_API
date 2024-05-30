# -*- coding: utf-8 -*-
import pickle
# from sklearn import tree
from sklearn.ensemble import ExtraTreesRegressor

from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
import datetime
import numpy as np
import logging
from ReadData import ReadData
from ReadConfig import ReadConfig
from datetime import datetime as dt, timedelta as delta
import json


class ThermalComfortHvac:
    """
    This Class
    1. trains the decision tree regressor.
    2. returns the thermal comfort model and score.
    3. appends new training data to a csv file.
    """

    def __init__(self, args, sav, train=False):
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
            "train_success": true
        }
        """
        try:
            if train:
                self.client = args["client"]
                self.training_set = args["training_set"]
            else:
                # TODO Inference?
                pass
            self.sav_file_path = sav
            self.modes = {
                "off": 0,
                "default": 1,
                "cool": 2,
                "heat": 3
            }
        except Exception as e:
            print("Exception in ThermalComfortHvac.__init__")
            logging.exception(e)

    def train(self):
        model, score = self._train_hvac_model()
        return model, score

    def predict(self, features):

        """Returns the predicted model output.

        :param features: contains all features

        :return: (int best_set_temp, int on_off) model prediction for the hvac setTemp and On/Off
        """
        try:
            temperature = features["temperature"]
            humidity = features["humidity"]
            temperature_out = features["temperature_out"]
            humidity_out = features["humidity_out"]
            thermal_comfort = features["thermal_comfort"]
            date = features["date"]

            pmv = pickle.load(open(self.sav_file_path, 'rb'))
            # TODO Change time features
            hour = date.hour
            week_day = date.weekday()
            day_of_year = date.timetuple().tm_yday

            hour_sin = np.sin(2 * np.pi * hour / 24)
            hour_cos = np.cos(2 * np.pi * hour / 24)

            week_day_sin = np.sin(2 * np.pi * week_day / 6)
            week_day_cos = np.cos(2 * np.pi * week_day / 6)

            day_of_year_sin = np.sin(2 * np.pi * day_of_year / 365)
            day_of_year_cos = np.cos(2 * np.pi * day_of_year / 365)

            inference = pmv.predict([[hour_sin, hour_cos, week_day_sin, week_day_cos, day_of_year_sin, day_of_year_cos,
                                      temperature, temperature_out, humidity, humidity_out, thermal_comfort]])

            heat = round(float(inference[0][0]))
            cool = round(float(inference[0][1]))
            mode = int(inference[0][2])
            if -20 > heat or heat > 40:
                print("heat set_temp out of range")
                return None, None, None
            if -20 > cool or cool > 40:
                print("cool set_temp out of range")
                return None, None, None
            if 0 > mode or mode > 4:
                print("mode out of range")
                return None, None, None
            return round(heat, 2), round(cool, 2), mode
        except Exception as e:
            print("Exception in ThermalComfortHvac.predict")
            logging.exception(e)
            return None, None

    def _train_hvac_model(self):
        """Trains the thermal comfort model and returns the
        model object and the model's score based on a training set split.

        :return: (Model model, String score) Returns the new model and its score.
        """
        try:
            x, y = self._create_hvac_training_set()
            model, score = self._train(x, y)
            return model, score
        except Exception as e:
            print("Exception in ThermalComfortHvac.train_pmv_model")
            logging.exception(e)
            return 'null', 'null'

    def _create_hvac_training_set(self):
        """Creates and returns the training set
        that will be used to train the thermal comfort model.

        :return: (Array x, Array y) Returns the thermal comfort training set
        """
        x = []
        y = []
        try:
            for row in self.training_set:
                date = str_to_dt(row[0])
                temperature = float(row[1])
                humidity = float(row[2])
                out_temperature = float(row[3])
                out_humidity = float(row[4])
                thermal_comfort = float(row[5])
                heat_temp = float(row[6])
                cool_temp = float(row[7])
                mode = float(row[8])

                hour = date.hour
                week_day = date.weekday()
                day_of_year = date.timetuple().tm_yday

                hour_sin = round(np.sin(2 * np.pi * hour / 24), 3)
                hour_cos = round(np.cos(2 * np.pi * hour / 24), 3)

                week_day_sin = round(np.sin(2 * np.pi * week_day / 6), 3)
                week_day_cos = round(np.cos(2 * np.pi * week_day / 6), 3)

                day_of_year_sin = round(np.sin(2 * np.pi * day_of_year / 365), 3)
                day_of_year_cos = round(np.cos(2 * np.pi * day_of_year / 365), 3)

                x.append(
                    [hour_sin, hour_cos, week_day_sin, week_day_cos, day_of_year_sin, day_of_year_cos,
                     temperature, out_temperature, humidity, out_humidity, thermal_comfort])
                y.append([heat_temp, cool_temp, mode])
            x = np.array(x)
        except Exception as e:
            print("Exception in ThermalComfortHvac.create_pmv_training_set")
            logging.exception(e)
        return x, y

    def _train(self, x, y):
        """Trains the decision tree regressor
        and returns the thermal comfort model and score

        :param Array x: Model training input data
        :param Array y: Model training output data

        :return: (Model model, String score) Returns the new model and its score.
        """
        # train model
        model = None
        score = None
        try:
            regressor = ExtraTreesRegressor(n_estimators=100, max_depth=12, n_jobs=1, random_state=0)
            # regressor = tree.DecisionTreeRegressor(max_depth=12, random_state=0)
            if x != [] and y != []:
                model = regressor.fit(x, y)
                pickle.dump(model, open(self.sav_file_path, 'wb'))

                # Get score with cross-validation
                reg_scores = cross_val_score(regressor, x, y, cv=10, scoring='neg_mean_squared_error')
                score = reg_scores.mean() * 100
            else:
                return None, None
        except Exception as e:
            print("Exception in ThermalComfortHvac.train")
            logging.exception(e)
        return model, score


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
