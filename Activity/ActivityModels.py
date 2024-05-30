from hmmlearn import hmm
import numpy as np
import configparser
import pickle
import logging
import pandas as pd
import os
from datetime import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import warnings

warnings.filterwarnings("ignore")


class ActivityModels:
    """Includes all the functions needed for the hidden Markov model 
    (train model,extract model, load model, predict model
    
    :param config : initializes the ConfigParser class which implements a 
       configuration language which provides the structure needed to read the data from 
       the ini file.
    """

    def __init__(self, args, files, train=False):
        """
        """
        try:
            self.data = args
            self.activity_config = args["activity_config"]
            self.general_config = args["general_config"]

            self.config = configparser.ConfigParser()
            self.config.read(self.activity_config)
            if "reinit" in self.data.keys():
                self.reinit = self.data["reinit"]
            else:
                self.reinit = False
            if self.reinit:
                self.reinit_config()
            self.client = self.data["client"]
            if train:
                self.training_set = args["training_set"]
                self.device_name = args["training_set"]["device_name"]
            else:
                self.device_name = args["device_name"]
            self.sav_rf = files["RF"]
            self.sav_hmm = files["HMM"]
        except Exception as e:
            logging.exception(e)

    def predict_state(self, value):
        """
        Predicts the state from a pretrained HMM model when current total
        consumption is given.

        """
        if type(value) is list:
            try:
                loaded_model = pickle.load(open(self.sav_hmm, 'rb'))
                value = np.array(value)
                prediction_state = loaded_model.predict(value.reshape(-1, 1))
                prediction = list(prediction_state)
                return prediction
            except Exception as e:
                logging.exception(e)
                print(e, "In HiddenMarkov.predict_state")
        else:
            try:
                loaded_model = pickle.load(open(self.sav_hmm, 'rb'))
                prediction_state = loaded_model.predict([[value]])
                prediction = int(prediction_state[0])
                return prediction
            except Exception as e:
                logging.exception(e)
                print(e, "In HiddenMarkov.predict_state", self.client, self.sav_hmm)
                return None

    def predict_activity(self, power):
        """
        Predicts the activity from a pretrained RF model when current device
        consumption is given. Predicted activity is associated with the device
        if is on. e.g washing machine=1 activity= washing clothes.

        :return int: predicted activity [0-1]
        """
        try:
            state = self.predict_state(power)
            max_d = int(self.config.get("devicesDuration", self.device_name))
            temp_d = int(self.config.get("tempDuration", self.device_name))
            if int(state) == 1 and temp_d < max_d:
                temp_d += 1
                self.activity_config.set("tempDuration", str(self.device_name), str(temp_d))
                with open(self.config, 'w') as f:
                    self.activity_config.write(f)
            if temp_d == max_d:
                self.activity_config.set("tempDuration", str(self.device_name), str(0))
                with open(self.config, 'w') as f:
                    self.activity_config.write(f)

            pred_list = [power, state, temp_d]
            df_obj = pd.DataFrame(pred_list)
            df_obj = df_obj.transpose()
            loaded_model = pickle.load(open(self.sav_rf, 'rb'))
            prediction = loaded_model.predict(df_obj)
            return int(prediction[0])
        except Exception as e:
            logging.exception(e)
            print(e, "In MyRandomForestClassifier.predict_activity")
            return None

    def train(self):
        models, msg = self._train_hmm()
        return models, msg

    def _train_hmm(self):
        """
        Creates automatically the initial occupancy profile based on the Hidden Markov states
        """

        power, power_tms = self._create_training_set(return_lists=True)
        # if len(power) < 9000:
        if len(power) < 2880:
            return [None, None], "Not enough data"
        try:
            _hmm = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=50)
            data = np.array([power])
            _hmm.fit(data.reshape(-1, 1))
            output = _hmm.predict([[0]])
            output = output[0]
            while output == 1:
                _hmm = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=50)
                data = np.array([power])
                _hmm.fit(data.reshape(-1, 1))
                output = _hmm.predict([[0]])
                output = output[0]
            value = np.array(power)
            states = _hmm.predict(value.reshape(-1, 1))
            states = list(states)
            pickle.dump(_hmm, open(self.sav_hmm, 'wb'))

            duration = [0] * (len(states))
            max_d = 0
            max_duration = 30
            for i in range(len(states)):
                if states[i] == 1:
                    max_d += 1
                    duration[i] = max_d
                if 30 >= max_d > 0 == states[i]:
                    max_d = 0
                    continue
            if max_d >= max_duration:
                max_duration = max_d
            if max_duration >= 30:
                max_duration = 30
            if max_duration == 0:
                max_duration = 5

            section = "devicesDuration"
            section_temp = "tempDuration"

            if not self.config.has_section(section):
                self.config.add_section(section)
            if not self.config.has_section(section_temp):
                self.config.add_section(section_temp)
            self.config.set(section, str(self.device_name), str(max_duration))
            self.config.set(section_temp, str(self.device_name), str(0))
            with open(self.activity_config, 'w') as f:
                self.config.write(f)
            times = []
            activity, timers = median(list(states), times, window=60)
            data = pd.DataFrame()
            data['consumption'] = list(power)
            data['state'] = states
            data['duration'] = duration
            data['activity'] = activity
            columns = [data.index.name] + [i for i in data]
            columns.pop(0)
            columns.pop(-1)
            x_train, x_test, y_train, y_test = train_test_split(data[columns], data['activity'], test_size=0.10,
                                                                random_state=4)
            _rf = RandomForestClassifier(n_estimators=200, max_depth=4, random_state=0)
            _rf.fit(x_train, y_train)
            pickle.dump(_rf, open(self.sav_rf, 'wb'))
            section = "Activity"
            last_train = "last_train"
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, last_train, dt_to_str(dt.now()))
            self.config.write(open(self.activity_config, "w"))
            return [_hmm, _rf], "ok"
        except Exception as e:
            logging.exception(e)
            print('In Activity_Inference_retrain')

    def _create_training_set(self, return_lists=False):
        """Creates and returns the training set
        that will be used to train the visual comfort model.

        :return: (Array x, Array y) Returns the visual comfort training set
        """
        try:
            if return_lists:
                power = []
                power_tms = []
                for row in self.training_set["device_power"]:
                    tms = str_to_dt(row[0])
                    var = float(row[1])
                    if tms is not None:
                        power.append(var)
                        power_tms.append(tms)
                return power, power_tms
            else:
                power_list = []
                for row in self.training_set["device_power"]:
                    tms = str_to_dt(row[0])
                    if tms is not None:
                        var = float(row[1])
                        power_list.append([var, tms])
                return power_list
        except Exception as e:
            print("Exception in Activity._create_training_set")
            logging.exception(e)

    def get_activity(self, power):
        """
        Gets all the data from the constructor parameters and calls all the
        functions needed to estimate Activity.

        :return string : The activity estimation results per device.
        The format of the string is:
           string= {'name':device_name,'activity':ac}
        """
        try:
            if not self.sav_rf or not self.sav_hmm:
                print('this returns none')
                return None
            print('this should be working')
            ac = self.predict_activity(power)
            response = {"activity": ac}
            return response
        except Exception as e:
            logging.exception(e)
            print(e, "In MyRandomForestClassifier.get_activity")
            return None

    def reinit_config(self):
        """
        Reinitialize config files if code is re-run
        :return:
        """
        self.config.set("Activity", "last_train", "2020-03-10T00:00:00.000Z")
        self.config.write(open(self.activity_config, "w"))
        return None

    def _create_hmm(self, filename, dataset):
        """Checks if the trained model from the training_phase function is valid
                and returns and extracts the valid trained HMM model as a .sav
                :param filename filename: the filename the HMM is saved
                :return model model: the trained HMM model
                """
        gm = self.training_phase(dataset)
        output = gm.predict([[0]])
        output = output[0]
        while output == 1:
            gm = self.training_phase(dataset)
            output = gm.predict([[0]])
            output = output[0]
        pickle.dump(gm, open(filename, 'wb'))
        return gm

    def training_phase(self, dataset):
        """Training phase of the Hidden Markov (HMM) model that trains and returns a pre-trained
        HMM model. This model is also saved.

        # """
        try:
            gm = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=50)
            data = np.array([dataset])
            gm.fit(data.reshape(-1, 1))
            return gm
        except Exception as e:
            print(e)
            return e

    def create_models(self):
        try:
            power_list = self._create_training_set()
            df = pd.DataFrame(power_list, columns=["device_power", "timestamp"])
            df['dt'] = pd.to_datetime(df['timestamp'])
            # Create a new string column (dd) from dt for the date without time
            df['dd'] = df['dt'].dt.strftime('%Y-%m-%d')
            dates = list(df['dd'].value_counts().index.values)
            counts = list(df['dd'].value_counts().values)
            df["device_power"] = df["device_power"].fillna(0)
            consumption = list(df["device_power"])
            if consumption is None or consumption == []:
                return None, None
            _hmm = self._create_hmm(self.sav_hmm, consumption)

            delete_days = []
            for i in range(len(dates)):
                # if counts[i] < 1440:
                if counts[i] < 56:
                    delete_days.append(dates[i])
                    # delete those days that the values are less than 1440
            if len(delete_days) != 0:
                for a in range(len(delete_days)):
                    filt = df['dd'] == delete_days[a]
                    df = df[~filt]
            dates.sort()
            dates = list(df['dd'].value_counts().index.values)
            range_days = len(dates)
            if range_days > 15:
                range_days = 15
            days_to_delete = []
            for e in range(len(dates)):
                if e > range_days:
                    days_to_delete.append(dates[e])
            if len(days_to_delete) != 0:
                for a in range(len(days_to_delete)):
                    filt = df['dd'] == days_to_delete[a]
                    df = df[~filt]

            df = df.reset_index(drop=True)
            df = df.sort_values('dt')
            dates = df['dd'].unique()
            dates = sorted(dates)
            power_n = list(df["device_power"])
            states_t = self.predict_state(power_n)
            states_try = list(states_t)
            df['states'] = states_try
            df['statesTry'] = states_try
            zlists = [0] * (len(df['statesTry']))
            df['duration'] = zlists
            max_duration = 0
            for i in range(range_days):
                max_d = 0
                d = dates[i]
                # Get all rows for d
                day_df = df[df['dd'] == d]
                # find wake up time and keep activity
                day_df['statesTry'] = list(median(list(day_df['statesTry']), 15)[0])
                #            plt.plot(day_df['statesTry'])
                for index, row in day_df.iterrows():
                    if row['statesTry'] == 1:
                        max_d += 1
                        day_df['duration'][index] = max_d
                    if 30 >= max_d > 0 == row['statesTry']:
                        max_d = 0
                        continue
                if max_d >= max_duration:
                    max_duration = max_d
                for idx, row in day_df.iterrows():
                    df.loc[idx, 'duration'] = row['duration']

            if max_duration >= 30:
                max_duration = 30
            if max_duration == 0:
                max_duration = 5

            config = configparser.ConfigParser()
            config.read(self.activity_config)
            section = "devicesDuration"
            section_temp = "tempDuration"

            if not config.has_section(section):
                config.add_section(section)
            if not config.has_section(section_temp):
                config.add_section(section_temp)
            with open(self.activity_config, 'w') as f:
                config.write(f)
            config.set(section, str(self.device_name), str(max_duration))
            config.set(section_temp, str(self.device_name), str(0))
            with open(self.activity_config, 'w') as f:
                config.write(f)

            data = pd.DataFrame()
            data['consumption'] = list(df["device_power"])
            data['state'] = list(df['states'])
            data['duration'] = list(df['duration'])
            data['activity'] = list(df['statesTry'])
            columns = [data.index.name] + [i for i in data]
            columns.pop(0)
            columns.pop(-1)
            x_train, x_test, y_train, y_test = train_test_split(data[columns], data['activity'], test_size=0.10,
                                                                random_state=4)
            _rf = RandomForestClassifier(n_estimators=200, max_depth=4, random_state=0)
            _rf.fit(x_train, y_train)
            pickle.dump(_rf, open(self.sav_rf, 'wb'))
            if not os.path.exists(self.sav_rf):
                os.remove(self.sav_hmm)
                return None, None
            return _rf, _hmm
        except Exception as e:
            logging.exception(e)
            print(e, " in ActivityModels.create_models")


def median(sequence, times, window=6):
    """
    Corrects a sequence of values with the use of a median filter
    :param times:
    :param list sequence: the list that will be corrected (sequence)
    :param int window: The size of the sliding window
    :return list: corrected sequence
    """
    try:
        size = len(sequence)
        middle_index = int((window - 1) / 2)
        for i in range(size):
            sort = []
            if i < (size - (window - 1)):
                for a in range(window):
                    sort.append(sequence[i + a])
                correction = int(np.median(sort))
                position = i + middle_index
                sequence[position] = correction
        return sequence, times
    except Exception as e:
        logging.exception(e)
        print(e, "In MyDecisionTreeClassifier.median")
        return None


def str_to_dt(st):
    """
    Converts a string object to datetime
    :param String st: date
    :return: datetime date
    """
    try:
        return dt.strptime(st, "%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.exception(e)


def dt_to_str(dat):
    try:
        return dat.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        logging.exception(e)
        return None
