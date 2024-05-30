import numpy as np
from scipy.optimize import curve_fit
import configparser
from suntime import Sun
from datetime import timedelta
import pytz
import json
import logging


class VisualComfort:
    """Estimates visual Comfort.
    :param self.config : initializes the ConfigParser class which implements a
    configuration language which provides the structure needed to read the ini
    file.
    """

    def __init__(self, path_to_config):
        try:
            self.config = configparser.ConfigParser()
            self.config.read(path_to_config)
        except Exception as e:
            logging.exception(e)
            print(e, "In VisualComfort.__init__")

    def visual_calculation(self, lux, latitude, longitude, timestamp):
        """Combines two models to estimate visual comfort the one model estimates
        visual comfort based on Hvidd's equation for visual comfort and the other
        model is based on EN12464-1 Standard scale of luminance that is fitted to [-3,3].
        :param timestamp:
        :param float lux: current Indoor luminance 
        :param float latitude:  latitude of the building 
        :param float longitude: longitude of the building
        :return float:  current visual comfort [-3,3]
        """
        try:
            listx1 = json.loads(self.config.get("visual", "xdata1"))
            xdata1 = np.array(listx1)
            listy1 = json.loads(self.config.get("visual", "ydata1"))
            ydata1 = np.array(listy1)
            z = np.polyfit(xdata1, ydata1, 3)
            ff = np.poly1d(z)
            listx2 = json.loads(self.config.get("visual", "xdata2"))
            xdata2 = np.array(listx2)
            listy2 = json.loads(self.config.get("visual", "ydata2"))
            ydata2 = np.array(listy2)
            popt2, pcov2 = curve_fit(self.fit_lux_values, xdata2, ydata2)
            listx3 = json.loads(self.config.get("visual", "xdata3"))
            xdata3 = np.array(listx3)
            listy3 = json.loads(self.config.get("visual", "ydata3"))
            ydata3 = np.array(listy3)
            popt3, pcov3 = curve_fit(self.fit_lux_values, xdata3, ydata3)
            listxln = json.loads(self.config.get("visual", "xdata1n"))
            xdata1n = np.array(listxln)
            listyln = json.loads(self.config.get("visual", "ydata1n"))
            ydata1n = np.array(listyln)
            zn = np.polyfit(xdata1n, ydata1n, 3)
            ffn = np.poly1d(zn)
            listx2n = json.loads(self.config.get("visual", "xdata2n"))
            xdata2n = np.array(listx2n)
            listy2n = json.loads(self.config.get("visual", "ydata2n"))
            ydata2n = np.array(listy2n)
            zn2 = np.polyfit(xdata2n, ydata2n, 3)
            ffn2 = np.poly1d(zn2)
            weight_model = self.set_day_night_weight(latitude, longitude, timestamp)
            g = self.daily_model_vc(lux)
            if weight_model < 0.6:
                if 0 <= lux <= 500:
                    f = float(ff(lux))
                elif 500 < lux <= 2000:
                    f = float(self.fit_lux_values(lux, *popt2))
                else:
                    f = float(self.fit_lux_values(lux, *popt3))
                visual_comfort = weight_model * f + (1 - weight_model) * g
            else:
                if 0 <= lux <= 500:
                    f = float(ffn(lux))
                else:
                    f = float(ffn2(lux))
                visual_comfort = weight_model * f + (1 - weight_model) * g
            visual_comfort = correct_thresholds(visual_comfort)
            return visual_comfort
        except Exception as e:
            logging.exception(e)
            print(e, "In VisualComfort.visual_calculation")
            return None

    def fit_lux_values(self, x, a, b, c):
        """Fits a list of lux values to a quadratic polynomial (ax^2+bx+c)
         needed for the curve fitting of the luminance EN12464-1 Standard
         scale to [-3,3].
         :param float x:  lux values
         :param float a:   coefficient of the quadratic equation
         :param float b:   coefficient of the quadratic equation
         :param float c:   coefficient of the quadratic equation
         return list: fitted lux values
         """
        try:
            return a * x ** 2 + b * x + c
        except Exception as e:
            print(e, "In VisualComfort.fit_lux_values")
            return None

    def daily_model_vc(self, lux):
        """Estimates visual comfort based on Hvidd's equation.
        :param float lux: current Indoor luminance
        :returns float: visual comfort [-3,3]
        """
        try:
            if lux is not None:
                if lux < 380:
                    vc = (-1 / 23940000) * (lux ** 3) + (1 / 79800) * (lux ** 2) + (1097 / 119700) * lux - 3
                else:
                    vc = 0.00096154 * lux - 0.36538  # Wienold
                return float(round(vc, 3))
            else:
                return None
        except Exception as e:
            logging.exception(e)
            print(e, "In VisualComfort.daily_model_vc")
            return None

    def set_day_night_weight(self, latitude, longitude, timestamp):
        """Gets current time and estimates if it is  night, twilight or daylight
        and estimates the weight the night model is going to be used.
        :param timestamp:
        :param float latitude: latitude  of the building  
        :param float longitude: longitude  of the building
        :return float: weight for the night model
        """
        try:
            now = timestamp
            utc = pytz.UTC
            now = now.replace(tzinfo=utc)
            sun = Sun(latitude, longitude)
            today_sunrise = sun.get_local_sunrise_time()
            today_sunset = sun.get_local_sunset_time()
            today_sunrise = today_sunrise.replace(tzinfo=utc)
            today_sunset = today_sunset.replace(tzinfo=utc)
            snr_asTw = today_sunrise - timedelta(seconds=6000)
            snr_asNaut = today_sunrise - timedelta(seconds=3840)
            snr_asCiv = today_sunrise - timedelta(seconds=1740)
            sns_as_CT = today_sunset + timedelta(seconds=1740)
            sns_as_Naut = today_sunset + timedelta(seconds=3840)
            sns_as_CIv = today_sunset + timedelta(seconds=6000)
            if (now >= today_sunrise) and (now <= today_sunset):
                weight_for_Nmodel = 0.4
            elif (now > snr_asTw) and (now < snr_asNaut):
                weight_for_Nmodel = 0.425
            elif (now >= snr_asNaut) and (now < snr_asCiv):
                weight_for_Nmodel = 0.450
            elif (now >= snr_asCiv) and (now < today_sunrise):
                weight_for_Nmodel = 0.475
            elif (now >= today_sunset) and (now < sns_as_CT):
                weight_for_Nmodel = 0.475
            elif (now >= sns_as_CT) and (now < sns_as_Naut):
                weight_for_Nmodel = 0.450
            elif (now >= sns_as_Naut) and (now < sns_as_CIv):
                weight_for_Nmodel = 0.425
            else:
                weight_for_Nmodel = 0.6
            return weight_for_Nmodel
        except Exception as e:
            logging.exception(e)
            print(e, "In VisualComfort.set_day_night_weight")
            return None


def correct_thresholds(value):
    """Corrects the comfort levels if they are beyond [-3,3]
    :param float value: estimated comfort value
    :return float: corrected comfort value [-3,3]
    """
    try:
        if value > 3:
            value = 3
        elif value < -3:
            value = -3
        return value
    except Exception as e:
        logging.exception(e)
        print(e, "In VisualComfort.correct_thresholds")
        return None
