# -*- coding: utf-8 -*-
import pickle
from sklearn import tree
from sklearn.model_selection import train_test_split
import csv
import datetime
import numpy as np
from datetime import datetime as dt, timedelta as delta
import logging


class ThermalComfortThermostat:
    """
    This Class
    1. trains the decision tree regressor.
    2. returns the thermal comfort model and score.
    3. appends new training data to a csv file.
    4. predicts dimmer values for the lights.
    """

    def __init__(self, args, sav, train=False):
        """
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
                "heat": 1
            }
        except Exception as e:
            print("Exception in ThermalComfortHvac.__init__")
            logging.exception(e)

    def train(self):
        model, score = self._train_thermostat_model()
        return model, score

    def predict(self, features):
        """Returns the predicted model output.
        param: features
        :return: (int best_set_temp, int on_off) model prediction for the hvac setTemp and On/Off
        """
        try:
            temperature = features["temperature"]
            humidity = features["humidity"]
            temperature_out = features["temperature_out"]
            humidity_out = features["humidity_out"]
            comfort = features["thermal_comfort"]
            date = features["date"]
            pmv = pickle.load(open(self.sav_file_path, 'rb'))

            hour = date.hour
            week_day = date.weekday()
            day_of_year = date.timetuple().tm_yday

            hour_sin = round(np.sin(2 * np.pi * hour / 24), 3)
            hour_cos = round(np.cos(2 * np.pi * hour / 24), 3)

            week_day_sin = round(np.sin(2 * np.pi * week_day / 6), 3)
            week_day_cos = round(np.cos(2 * np.pi * week_day / 6), 3)

            day_of_year_sin = round(np.sin(2 * np.pi * day_of_year / 365), 3)
            day_of_year_cos = round(np.cos(2 * np.pi * day_of_year / 365), 3)

            inference = pmv.predict([[hour_sin,
                                      hour_cos,
                                      week_day_sin,
                                      week_day_cos,
                                      day_of_year_sin,
                                      day_of_year_cos,
                                      temperature,
                                      humidity,
                                      temperature_out,
                                      humidity_out,
                                      comfort]])
            inference = inference[0]
            set_temp = float(inference[0])
            set_temp = round(set_temp * 2) / 2
            on_off = int(inference[1])

            if -20 > set_temp or set_temp > 40:
                print("cool set_temp out of range")
                return None, None
            if 0 > on_off or on_off > 4:
                print("on_off out of range")
                return None, None
            return set_temp, on_off
        except Exception as e:
            print("Exception in ThermalComfortHvac.predict")
            logging.exception(e)

    def _train_thermostat_model(self):
        """Trains the thermal comfort model and returns the
        model object and the model's score based on a training set split.

        :return: (Model model, String score) Returns the new model and its score.
        """

        try:
            x, y = self._create_thermostat_training_set()
            model, score = self._train(x, y)
            return model, score
        except Exception as e:
            print("Exception in ThermalComfortHvac.train_pmv_model")
            logging.exception(e)
            return 'null', 'null'

    def _create_thermostat_training_set(self):
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
                comfort = float(row[5])
                set_temp = float(row[6])
                mode = float(row[7])

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
                     temperature, out_temperature, humidity, out_humidity, comfort])
                y.append([set_temp, mode])
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
            if x != [] and y != []:
                regressor = tree.DecisionTreeRegressor()
                model = regressor.fit(x, y)
                pickle.dump(model, open(self.sav_file_path, 'wb'))
                # get_score
                x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
                test_model = regressor.fit(x_train, y_train)
                score = test_model.score(x_test, y_test)
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
