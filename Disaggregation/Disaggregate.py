import pandas as pd
import configparser
import numpy as np
import logging
import warnings
from datetime import datetime as dt

warnings.filterwarnings("ignore")


class Disaggregate:
    """
    Disaggregates the total power consumption for all the available devices of a house at a specific timestamp
    
    """

    def __init__(self, path_to_models, config_file):
        """
        Initiializes all necessary variables for the disaggregation class
        :param path object path_to_models: path to the pre-trained device models
        :param path object config_file: config file path
        """
        try:
            self.path_to_models = path_to_models
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
            self.lookbacks = self.config['Lookback_steps']
            self.thresholds = self.config['Device_thresholds']
        except Exception as e:
            logging.exception(e)
            print(e, "In Disaggregat.__init__")

    def run(self, args):
        """ 
        Runs the whole process of the disaggregation algorithm (feature extraction, prediction, return values)
        :return dict : disaggregated_data
        
        """
        try:
            disaggregated_data = {}
            data = convert_data_from_api(args["power_list"])
            available_devices = args["devices"]

            if data is not None:
                for device in available_devices:
                    model = self.get_model(device)
                    if model:
                        lookback = int(self.lookbacks[device])
                        threshold = int(self.thresholds[device])
                        temporal_features = create_temporal_features(lookback, data)
                        features = pd.concat([data, temporal_features], axis=1)

                        time_features = create_time_features(features)
                        features = pd.concat([features, time_features], axis=1)

                        features = drop_unnecessary_features(features)
                        predicted_value = predict(model, features)
                        pred = check_threshold(predicted_value[0], threshold)
                        disaggregated_data[device] = round(float(pred), 2)

            return disaggregated_data
        except Exception as e:
            logging.exception(e)
            print(e, "In Disaggregate.run")
            return None

    def get_model(self, device):
        """ 
        Gets the pre-trained model for the current device
        :param str device: current occupancy
        :return object : model
            
        """
        try:
            if device in self.path_to_models.keys():
                model = self.path_to_models[device]
            else:
                model = None
            return model
        except Exception as e:
            logging.exception(e)
            print(self.path_to_models.keys(), device)
            print(e, "In Disaggregat.get_model")


def convert_data_from_api(data):
    dates, active, reactive = [], [], []
    for i in range(len(data)):
        thisdate = dt.strptime(data[i][0], '%Y-%m-%d %H:%M:%S')
        activeval = data[i][1]
        reactiveval = data[i][2]

        dates.append(thisdate)
        active.append(activeval)
        reactive.append(reactiveval)

        return_df = pd.DataFrame(list(zip(dates, active, reactive)), columns=['ctime', 'P', 'Q'])
        return_df.index = return_df.ctime
        return_df.fillna(method='bfill', inplace=True)
        # return_df = return_df.resample('1min').bfill().interpolate()

    return return_df


def check_threshold(value, thresh):
    """
    Checks whether the predicted value is below the permitted threshold value, for the current device
    :param float value: predicted disaggregated consumption value for current device
    :param float thresh: consumption threshold for current device
    :return float value : predicted disaggregated consumption for current device after threshold correction
    """
    try:
        if value is not None:
            if value < thresh:
                value = 0
            return value
        else:
            return value
    except Exception as e:
        logging.exception(e)
        print(e, "In Disaggregat.check_threshold")


def create_time_features(data):
    """
    Creates features that represent the current timestamp's hour and weekday
    :param dataframe data: consumption data for current home
    :return dataframe : time_features

    """
    try:
        timestamps = list(data.index)

        hour = [timestamps[i].hour for i in range(len(timestamps))]
        week_day = [timestamps[i].weekday() for i in range(len(timestamps))]

        hour_sin = [np.sin(2 * np.pi * hour[i] / 24) for i in range(len(hour))]
        hour_cos = [np.cos(2 * np.pi * hour[i] / 24) for i in range(len(hour))]

        # week_day_sin = [np.sin(2 * np.pi * week_day[i] / 24) for i in range(len(week_day))]
        # week_day_cos = [np.cos(2 * np.pi * week_day[i] / 24) for i in range(len(week_day))]

        time_features = pd.DataFrame(np.column_stack([hour_sin, hour_cos]),
                                     columns=['Hour_sin', 'Hour_cos'])
        time_features.index = data.index
        return time_features
    except Exception as e:
        logging.exception(e)
        print(e, "In Disaggregat.create_time_features")


def create_temporal_features(lookback, data):
    """
    Creates the temporal features for the current device according to the lookback steps for this device
    :param int lookback: the number of lookback steps for this device
    :param data:
    :return dataframe : temporal_feat

    """
    try:
        new_cols = []
        col_names = data.columns
        temporal_feat = pd.DataFrame()
        for i in range(lookback):
            temp = data.shift(i + 1)
            temporal_feat = pd.concat([temporal_feat, temp], axis=1)
            for j in range(len(col_names)):
                new_cols.append(col_names[j] + '_diff_' + str(i + 1))
            temporal_feat.columns = new_cols
        return temporal_feat
    except Exception as e:
        logging.exception(e)
        print(e, "In Disaggregat.create_temporal_features")


def drop_unnecessary_features(features):
    """
    Drops the features that are not used in the predictive model
    :param dataframe features: current occupancy
    :return dataframe :  features

    """
    try:
        cols = features.columns
        cols_to_drop = [cols[i] for i in range(len(cols)) if 'ctime' in cols[i]]
        features = features.drop(cols_to_drop, axis=1)
        return features
    except Exception as e:
        logging.exception(e)
        print(e, "In Disaggregat.drop_unecessary_features")


def predict(model, features):
    """
    Predicts the disaggregated consumption for the current device
    :param object model: the device's pre-trained disaggregation model
    :param dataframe features: total extracted features
    :return float :  disaggregated_consumption

    """
    try:
        disaggregated_consumption = model.predict(features.iloc[[-1]])
        return disaggregated_consumption
    except Exception as e:
        logging.exception(e)
        print(e, "In Disaggregat.predict")
