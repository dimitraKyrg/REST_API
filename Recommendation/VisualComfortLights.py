# -*- coding: utf-8 -*-
import pickle
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import datetime
import numpy as np
import logging
from datetime import datetime as dt, timedelta as delta


class VisualComfortLights:
    """
    This Class
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
        except Exception as e:
            print("Exception in VisualComfortLights.__init__")
            logging.exception(e)

    def train(self):
        model, score = self._train_lights_model()
        return model, score

    def predict(self, features):
        """Returns the predicted model output.
        :param features:
        :return: (int best_dimmer) model prediction for the dimmer of the lights.
        """
        try:
            vcm = pickle.load(open(self.sav_file_path, 'rb'))

            luminance = features["luminance"]
            ghi = features["ghi"]
            visual_comfort = features["visual_comfort"]
            date = features["date"]

            hour = date.hour
            week_day = date.weekday()
            day_of_year = date.timetuple().tm_yday

            hour_sin = round(np.sin(2 * np.pi * hour / 24), 3)
            hour_cos = round(np.cos(2 * np.pi * hour / 24), 3)

            week_day_sin = round(np.sin(2 * np.pi * week_day / 6), 3)
            week_day_cos = round(np.cos(2 * np.pi * week_day / 6), 3)

            day_of_year_sin = round(np.sin(2 * np.pi * day_of_year / 365), 3)
            day_of_year_cos = round(np.cos(2 * np.pi * day_of_year / 365), 3)

            inference = vcm.predict([[hour_sin,
                                      hour_cos,
                                      week_day_sin,
                                      week_day_cos,
                                      day_of_year_sin,
                                      day_of_year_cos,
                                      luminance,
                                      ghi,
                                      visual_comfort]])
            inference = inference[0]
            dimmer = int(inference[0])
            on_off = int(inference[1])

            if dimmer > 100:
                dimmer = 100
            elif dimmer < 0:
                dimmer = 0
            dimmer = round(dimmer, -1)
            if dimmer == 0:
                dimmer = 10
            if on_off != 0 and on_off != 1:
                print("on_off out of range")
                return None, None
            return dimmer, on_off
        except Exception as e:
            print("Exception in VisualComfortLights.predict")
            logging.exception(e)
            return None

    def _train_lights_model(self):
        """Trains the visual comfort model and returns the
        model object and the model's score based on a training set split.

        :return: (Model model, String score) Returns the new model and its score.
        """
        try:
            x, y = self._create_lights_training_set()
            model, score = self._train(x, y)
            return model, score
        except Exception as e:
            print("Exception in VisualComfortLights.train_vcm_model")
            logging.exception(e)
            return 'null', 'null'

    def _create_lights_training_set(self):
        """Creates and returns the training set
        that will be used to train the visual comfort model.

        :return: (Array x, Array y) Returns the visual comfort training set
        """
        x = []
        y = []
        try:
            for row in self.training_set:
                date = str_to_dt(row[0])
                lux = float(row[1])
                ghi = float(row[2])
                vcm = float(row[3])
                dimmer = float(row[4])
                on_off = float(row[5])

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
                     lux, ghi, vcm])
                y.append([dimmer, on_off])
            x = np.array(x)
        except Exception as e:
            print("Exception in VisualComfortLights.create_visual_training_set")
            logging.exception(e)
        return x, y

    def _train(self, x, y):
        """Trains the random forest regressor
        and returns the visual comfort model and score

        :param Array x: Model training input data
        :param Array y: Model training output data

        :return: (Model model, String score) Returns the new model and its score.
        """
        model = None
        score = None
        try:
            # train model
            regressor = RandomForestRegressor(max_depth=7, random_state=1, n_estimators=100)
            model = regressor.fit(x, y)
            pickle.dump(model, open(self.sav_file_path, 'wb'))
            # get_score
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=0)
            test_model = regressor.fit(x_train, y_train)
            print('i got in train')
            print(x_test, y_test)
            score = test_model.score(x_test, y_test)
            print('after score')
        except Exception as e:
            print("Exception in VisualComfortLights.train")
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
