from hmmlearn import hmm
import numpy as np
import configparser
import pickle
import logging
from datetime import datetime as dt
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import os
import sklearn.tree


class OccupancyModels:
    """
    Includes all the functions needed for the hidden Markov model
    (train model,extract model, load model, predict model
    
    :param self.config : initializes the ConfigParser class which implements a
       configuration language which provides the structure needed to read the data from 
       the ini file.
    """

    def __init__(self, args, files, train=False):
        try:
            self.args = args
            self.client = args["client"]
            if train:
                self.training_set = args["training_set"]
            else:
                # TODO Inference?
                pass
            self.sav_dt = files["DT"]
            self.sav_hmm = files["HMM"]
            self.path_to_config = args["config_file"]
            self.config = configparser.ConfigParser()
            self.config.read(self.path_to_config)
        except Exception as e:
            logging.exception(e)

    def train(self):
        hmm_model, dtc_model = self._train_hmm()
        return hmm_model, dtc_model

    def predict_hmm(self, value):
        """
        Predicts the state from a pretrained HMM model when current total
        consumption is given.
        :return int: predicted state 0/1
        """
        try:
            
            if type(value) is list:

                loaded_model = pickle.load(open(self.sav_hmm, 'rb'))
                value = np.array(value)
                prediction_state = loaded_model.predict(value.reshape(-1, 1))
                prediction = list(prediction_state)
                return prediction
            else:
                loaded_model = pickle.load(open(self.sav_hmm, 'rb'))
                prediction_state = loaded_model.predict([[value]])
                prediction = int(prediction_state[0])
                return prediction
        except Exception as e:
            logging.exception(e)
            print(e, "In HiddenMarkov.predict_state else", self.sav_hmm)
            return None

    def predict_occupancy(self, consumption, timestamp):
        """
        Predicts the occupancy from a pretrained DT model when current total
        consumption is given. Predicted occupancy is 0:absent, 1:sleeping, activity
        """
        try:
            date = timestamp
            hour = date.hour
            minute = date.minute
            weekend = day_of_the_week(timestamp)
            state = self.predict_hmm(consumption)
            pred_list = [hour, minute, weekend, consumption, state]
            df_obj = pd.DataFrame(pred_list)
            df_obj = df_obj.transpose()
            loaded_model = pickle.load(open(self.sav_dt, 'rb'))
            prediction = loaded_model.predict(df_obj)
            return int(prediction[0])
        except Exception as e:
            logging.exception(e)
            print(e, "In MyDecisionTreeClassifier.predict_occupancy")
            return None

    def _train_hmm(self):
        """Retrains the HMM, DT models"""
        try:
            occ, occ_tms, power, power_tms = self._create_training_set()
            
            if len(power) < 9000 or len(occ) < 9000:
                return None

            timestamps = []
            occupancy = []
            consumption_n = []
            print(f'occ_tms is : {len(occ_tms)}, power_tms is : {len(power_tms)}')
            a = 0
            if len(occ_tms) >= len(power_tms):
                for i in range(len(power_tms)):
                    if power_tms[i] == occ_tms[a]:
                        timestamps.append(occ_tms[i])
                        occupancy.append(occ[a])
                    else:
                        while power_tms[i] != occ_tms[a]:
                            a = a + 1
                        timestamps.append(occ_tms[i])
                        occupancy.append(occ[a])
            if len(occ_tms) < len(power_tms):
                print('ok')
                for i in range(len(occ_tms)):
                    if occ_tms[i] == power_tms[a]:
                        timestamps.append(occ_tms[i])
                        consumption_n.append(power[a])
                    else:
                        while occ_tms[i] == power_tms[a]:
                            a = a + 1
                        timestamps.append(occ_tms[i])
                        consumption_n.append(power[a])
                power = list(consumption_n)
                occupancy = list(occ)
                occupancy = median(list(occupancy), window=40)
            _gm = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=5)
            data = np.array([power])
            _gm.fit(data.reshape(-1, 1))
            output = _gm.predict([[0]])
            output = output[0]
            while output == 1:
                _gm = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=5)
                data = np.array([power])
                _gm.fit(data.reshape(-1, 1))
                output = _gm.predict([[0]])
                output = output[0]
            value = np.array(power)
            states = _gm.predict(value.reshape(-1, 1))
            states = list(states)
            pickle.dump(_gm, open(self.sav_hmm, 'wb'))

            data = pd.DataFrame()
            data['hour'] = [date.hour for date in timestamps]
            data['minutes'] = [date.minute for date in timestamps]
            weekdays = [date.weekday() for date in timestamps]
            weekend = weekends(weekdays)
            data['weekend'] = weekend
            data['consumption'] = power
            data['state'] = states
            data['occupancy'] = occupancy
            last_value = timestamps[-1]
            last_value = dt_to_str(last_value)
            columns = [data.index.name] + [i for i in data]
            columns.pop(0)
            columns.pop(-1)

            x_train, x_test, y_train, y_test = train_test_split(data[columns],
                                                                data['occupancy'],
                                                                test_size=0.1,
                                                                random_state=4)
            _dt = DecisionTreeClassifier(max_depth=20)
            _dt.fit(x_train, y_train)
            pickle.dump(_dt, open(self.sav_dt, 'wb'))
            section = "Occupancy"
            last_train = "last_train"
            if not self.config.has_section(section):
                self.config.add_section(section)
            self.config.set(section, str(last_train), last_value)
            self.config.write(open(self.path_to_config, "w"))

            return _gm, _dt
        except Exception as e:
            logging.exception(e)
            print('In occupancyInference.config')

    def _create_training_set(self, occupancy=True):
        """Creates and returns the training set
        that will be used to train the visual comfort model.

        :return: (Array x, Array y) Returns the visual comfort training set
        """
        try:
            print(' i got in create training set')
            if occupancy:
                occ = []
                occ_tms = []
                power = []
                power_tms = []
                print('before for')
                for row in self.training_set["occupancy"]:
                    print('i got in here 1')
                    tms = str_to_dt(row[0])
                    var = int(row[1])
                    occ.append(var)
                    occ_tms.append(tms)
                for row in self.training_set["mains_power"]:
                    print('i got in here 2')
                    tms = str_to_dt(row[0])
                    var = float(row[1])
                    power.append(var)
                    power_tms.append(tms)
                return occ, occ_tms, power, power_tms
            else:
                power_list = []
                for row in self.training_set["mains_power"]:
                    tms = str_to_dt(row[0])
                    var = float(row[1])
                    power_list.append([var, tms])
                    # power_tms.append(tms)
                return power_list
        except Exception as e:
            print("Exception in VisualComfortLights.create_visual_training_set")
            logging.exception(e)

    def _create_hmm(self, filename, list_t):
        """Checks if the trained model from the training_phase function is valid
        and returns and extracts the valid trained HMM model as a .sav
        :param filename filename: the filename the HMM is saved
        :param list_t:
        :return model model: the trained HMM model
        """
        gm = training_phase(list_t)
        output = gm.predict([[0]])
        output = output[0]
        while output == 1:
            gm = training_phase(list_t)
            output = gm.predict([[0]])
            output = output[0]
        pickle.dump(gm, open(filename, 'wb'))
        return gm

    def create_models(self):
        file_dt = self.sav_dt
        filen_oc = self.sav_hmm

        power_list = self._create_training_set(occupancy=False)

        df = pd.DataFrame(power_list, columns=["power", "timestamp"])

        # df['timestamp'] = pd.to_datetime(df['ctime'], infer_datetime_format=True)
        # Convert timestamp column to python datetime object - Create new column dt
        # TODO maybe delete?
        df['dt'] = pd.to_datetime(df['timestamp'])

        # Create a new string column (dd) from dt for the date without time
        df['dd'] = df['dt'].dt.strftime('%Y-%m-%d')
        dates = list(df['dd'].value_counts().index.values)
        counts = list(df['dd'].value_counts().values)
        df["power"] = df["power"].fillna(0)
        consumption = list(df["power"])
        _hmm = self._create_hmm(filen_oc, consumption)

        # find which dates to delete
        delete_days = []
        for i in range(len(dates)):
            if counts[i] < 96:
                delete_days.append(dates[i])
            # delete those days that the values are less than 1440
        if len(delete_days) != 0:
            for a in range(len(delete_days)):
                filt = df['dd'] == delete_days[a]
                df = df[~filt]

        dates.sort()
        dates = list(df['dd'].value_counts().index.values)

        range_days = len(dates)
        if range_days > 7:
            range_days = 7
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
        consumption_n = list(df["power"])
        states_t = self.predict_hmm(consumption_n)
        states_try = list(states_t)
        hours = hour(df['timestamp'])
        df['states'] = states_try
        df['statesTry'] = states_try
        df['hours'] = hours
        for i in range(range_days):
            d = dates[i]
            # Get all rows for d
            day_df = df[df['dd'] == d]
            # find wake up time and keep activity
            wakeup = 0
            for index, row in day_df.iterrows():
                if 5 <= row['hours'] < 11 and row['statesTry'] == 1:
                    for a in range(50):
                        day_df['statesTry'][index + a] = 2
                        wakeup = (index + a) - 49
                    break

            day_df['statesTry'] = list(median_create(list(day_df['statesTry']), window=50))

            # check if there is any activity
            activity = False
            for index, row in day_df.iterrows():
                if row['hours'] >= 10 and row['statesTry'] == 1:
                    activity = True
                    break

            if activity == False and wakeup == 0:
                continue

            # Activity time
            for index, row in day_df.iterrows():
                if row['statesTry'] == 1:
                    day_df['statesTry'][index] = 2

            if wakeup != 0:
                for index, row in day_df.iterrows():
                    if index <= wakeup and row['statesTry'] == 0:
                        day_df['statesTry'][index] = 1
                    # plt.plot( day_df['statesTry'])

            sleep_time = 0
            if activity:
                for index, row in day_df.iterrows():
                    if row['hours'] >= 22 and row['statesTry'] == 2:
                        sleep_time = index
                        break
            if activity and sleep_time != 0:
                for index, row in day_df.iterrows():
                    if index >= sleep_time and row['statesTry'] == 0:
                        sleep_time = index
                        break

            if activity and sleep_time != 0:
                for index, row in day_df.iterrows():
                    if index >= sleep_time and row['statesTry'] == 0:
                        day_df['statesTry'][index] = 1

            day_df['statesTry'] = list(median_create(list(day_df['statesTry']), window=50))
            for idx, row in day_df.iterrows():
                df.loc[idx, 'statesTry'] = row['statesTry']
        weeknds = weekend(df['timestamp'])
        data = pd.DataFrame()
        data['hour'] = df['timestamp'].dt.hour
        data['minutes'] = df['timestamp'].dt.minute
        data['weekend'] = weeknds
        data['consumption'] = list(df["power"])
        data['state'] = list(df['states'])
        data['occupancy'] = df['statesTry']
        columns = [data.index.name] + [i for i in data]
        columns.pop(0)
        columns.pop(-1)
        x_train, x_test, y_train, y_test = train_test_split(data[columns], data['occupancy'], test_size=0.1,
                                                            random_state=4)
        _dt = DecisionTreeClassifier(max_depth=20)
        _dt.fit(x_train, y_train)
        pickle.dump(_dt, open(file_dt, 'wb'))
        if not os.path.exists(file_dt):
            os.remove(filen_oc)
        return _dt, _hmm


def median_create(sequence, window):
    """Corrects a sequence of values with the use of a median filter

    :param list sequence: the list that will be corrected (sequence)
    :param int window: The size of the sliding window
    :return list: corrected sequence        """
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
    return sequence


def training_phase(list_t):
    """Training phase of the Hidden Markov (HMM) model that trains and returns a pre-trained
    HMM model. This model is also saved.
    :param filename filename: the filename the HMM is goind to be saved as
    :param list_t:

    :return model model: the trained HMM model
    # """
    dataset = list_t
    try:
        gm = hmm.GaussianHMM(n_components=2, covariance_type='full', n_iter=50)
        data = np.array([dataset])
        gm.fit(data.reshape(-1, 1))
        return gm
    except Exception as e:
        print(e)
        return 0


def day_of_the_week(timestamp):
    """
    Gets current day and checks the weekday and returns if the current
    day is weekend or not
    :return boolean:  weekend or not
    """
    try:
        weekno = timestamp.weekday()
        if weekno < 5:
            weekend = 0
        else:
            weekend = 1
        return weekend
    except Exception as e:
        logging.exception(e)
        print(e, "In MyDecisionTreeClassifier.day_of_the_week")
        return None


def weekends(date):
    wknds = []
    for d in date:
        if d < 5:
            wknds.append(0)
        else:
            wknds.append(1)
    return wknds


def weekend(data):
    """ Gets current list of dates and checks the weekday and returns if the current
    day is weekend or not

    :return boolean:  weekend or not
    """
    weekends = []
    for i in range(len(data)):
        d = data[i]
        w = day_of_the_week(d)
        weekends.append(w)
    return weekends


def hour(data):
    """Gets a list with timestamps and returns the hour part"""
    hours = []
    for i in range(len(data)):
        h = data[i].hour
        hours.append(h)
    return hours


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
            return temp
        else:
            return None
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
