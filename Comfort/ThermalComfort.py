import configparser
from sympy import Symbol
from sympy import solve
import numpy as np
import logging


class ThermalComfort:
    """Εstimates thermal comfort.
    """

    def __init__(self, path_to_config):
        try:
            self.config = configparser.ConfigParser()
            self.config.read(path_to_config)
            self.thermal_adjust = float(self.config.get('coefficients', 'thermalAdjust'))
            self.activity_clothing = {
                "spring": {
                    "1": {
                        "clothing": 1.35,
                        "metabolic": 40
                    },
                    "2": {
                        "clothing": 0.83,
                        "metabolic": 65
                    },
                    "3": {
                        "clothing": 0.83,
                        "metabolic": 60
                    },
                    "4": {
                        "clothing": 0.83,
                        "metabolic": 65
                    },
                    "5": {
                        "clothing": 1.05,
                        "metabolic": 45
                    },
                },
                "autumn": {
                    "1": {
                        "clothing": 1.35,
                        "metabolic": 40
                    },
                    "2": {
                        "clothing": 0.83,
                        "metabolic": 65
                    },
                    "3": {
                        "clothing": 0.83,
                        "metabolic": 60
                    },
                    "4": {
                        "clothing": 0.83,
                        "metabolic": 65
                    },
                    "5": {
                        "clothing": 1.05,
                        "metabolic": 45
                    },
                },
                "winter": {
                    "1": {
                        "clothing": 1.61,
                        "metabolic": 40
                    },
                    "2": {
                        "clothing": 1.01,
                        "metabolic": 65
                    },
                    "3": {
                        "clothing": 1.01,
                        "metabolic": 60
                    },
                    "4": {
                        "clothing": 1.01,
                        "metabolic": 65
                    },
                    "5": {
                        "clothing": 1.31,
                        "metabolic": 45
                    },
                },
                "summer": {
                    "1": {
                        "clothing": 0.87,
                        "metabolic": 40
                    },
                    "2": {
                        "clothing": 0.57,
                        "metabolic": 65
                    },
                    "3": {
                        "clothing": 0.57,
                        "metabolic": 60
                    },
                    "4": {
                        "clothing": 0.57,
                        "metabolic": 65
                    },
                    "5": {
                        "clothing": 0.72,
                        "metabolic": 45
                    },
                },
            }
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.__init__")

    def calculate_season(self, timestamp):
        """Gets current month from current datetime and estimates current season.
        :return string: current season    
        """
        try:
            date = timestamp
            m = date.month
            if m == 1 or m == 2 or m == 12:
                s = "winter"
            elif 3 <= m <= 5:
                s = "spring"
            elif 6 <= m <= 8:
                s = "summer"
            else:
                s = "autumn"
            return s
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.calculate_season")
            return None

    def calculate_interhalf(self, timestamp):
        """Gets current hour from current datetime and estimates the current time 
        interval from 5 predefined time-zones [1-5]. The time-zones are 1: 0:00-7:59,
        2: 8:00-11:59,3: 12:00-15:59, 4: 16:00-19:59 5: 20:00-23:59 and are  used for
        estimating different clothing insulation and metabolic rate values during the day.
        :return int:  current interval 
        """
        try:
            date = timestamp
            h = date.hour
            if 0 <= h < 8:
                intervalf = 1
            elif 8 <= h < 12:
                intervalf = 2
            elif 12 <= h < 16:
                intervalf = 3
            elif 16 <= h < 20:
                intervalf = 4
            else:
                intervalf = 5
            return str(intervalf)
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.calculate_interhalf")
            return None

    def clothing_by_temperature(self, temp):
        """Gets current  temperature and estimates clothing insulation related to 
        temperature.
        :param float temp: current temperature
        :return float:  clothing insulation 
        """
        try:
            clothing = 89.279 * (pow(temp, -1.592))
            clothing = round(clothing, 2)
            return clothing
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.clothing_by_temperature")
            return None

    def activity_by_temperature(self, temp):
        """Gets current  temperature and estimates metabolic rate related to 
        temperature.
        :param float temp:  current temperature
        :return float:  metabolic rate 
        """
        try:
            activity = 3081.90 * (pow(temp, -1.173))
            activity = int(activity)
            return activity
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.activity_by_temperature")
            return None

    def clothing_adjustment(self, temperature, timestamp):
        """Calculates the adjusted clothing  insulation. Clothing insulation is 
        estimated from the ASHRAE tables and by temperature with a pre-defined 
        weight (thermalAdjust) which is loaded from the ini file.
        :param float temperature:  current temperature
        :param Datetime timestamp:
        :return float:   adjusted estimated clothing insulation 
        """
        try:
            icl_season = self.clothing_by_season(timestamp)
            icl_temp = self.clothing_by_temperature(temperature)
            clothing = self.thermal_adjust * icl_season + (1 - self.thermal_adjust) * icl_temp
            return clothing
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.clothing_adjustment")
            return None

    def activity_adjustment(self, temperature, timestamp):
        """Calculates the adjusted metabolic rate. Metabolic rate is estimated 
        from the ASHRAE tables and by temperature with a pre-defined weight 
        (thermalAdjust) which is loaded from the ini file.
        :param float temperature: current temperature
        :param Datetime timestamp:
        :return float:  adjusted estimated metabolic rate       
        """
        try:
            m_season = self.activity_by_season(timestamp)
            m_temp = self.activity_by_temperature(temperature)
            activity = self.thermal_adjust * m_season + (1 - self.thermal_adjust) * m_temp
            return activity
        except Exception as e:
            print(e, "In ThermalComfort.activity_adjustment")
            logging.exception(e)
            return None

    def clothing_by_season(self, timestamp):
        """Gets clothing insulation from a saved file with the ASHRAE values 
        based on the current season and time.
        :param Datetime timestamp:
        saved values are per 5 predefined time-zones [1-5] and per season.
        :return float:  ASHRAE clothing insulation 
        """
        try:
            season = self.activity_clothing[self.calculate_season(timestamp)]
            intervalf = season[self.calculate_interhalf(timestamp)]
            return float(intervalf["clothing"])
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.clothing_by_season")
            return 0

    def activity_by_season(self, timestamp):
        """Estimates metabolic rate from a saved file with the ASHRAE values 
        based on the current season and time.
        :param Datetime timestamp:
        :return float:  ASHRAE metabolic rate   
        """
        try:
            season = self.activity_clothing[self.calculate_season(timestamp)]
            intervalf = season[self.calculate_interhalf(timestamp)]
            return int(intervalf["metabolic"])
        except Exception as e:
            logging.exception(e)
            return 0

    def thermal_calculation(self, ta, rh, icl, m):
        """Solves Fangers equation for thermal comfort estimation.
        :param float ta:  Indoor temperature 
        :param float rh:  Indoor Humidity 
        :param float icl:  Clothing Insulation  
        :param float m:  Metabolic rate(M)
        :return float: thermal comfort [-3,3] 
        """
        try:
            if ta is not None and rh is not None:
                psat = (0.782 + 2.962 * ta / 100 + 6.29 * (ta / 100) ** 2.325) ** 2  # in kPa
                pa = rh * psat / 100  # in kPa
                ec = 3.05 * (5.73 - 0.007 * m - pa) + 0.42 * (m - 58.15)  # also called Esk (E_skin)
                c_eres = 0.0014 * m * (34 - ta) + 0.0173 * m * (5.87 - pa)
                rcl = 0.155 * icl  # in W/m2
                if rcl >= 0.0775:
                    fcl = 1.05 + 0.1 * icl
                else:
                    fcl = 1 + 0.2 * icl
                va = 0.1  # example (in m/s)
                hc = 12.1 * va ** 0.5
                tsk = 35.7 - 0.0275 * m
                t = Symbol('t')
                tcl = solve(t - tsk + rcl * (fcl * hc * (t - ta) + 5.67 * 10 ** (-8) * 0.95 * 0.77 * fcl * (
                        (t + 273) ** 4 - (ta + 273) ** 4)), t)  # considering radiant temp equal to air temp
                if len(tcl) > 1:
                    c = fcl * hc * (tcl[1] - ta)
                    r = 3.96 * 10 ** (-8) * fcl * ((tcl[1] + 273) ** 4 - (ta + 273) ** 4)
                    l1 = m - c - r - c_eres - ec
                    pmv = l1 * (0.303 * np.exp(-0.036 * m) + 0.028)
                    pmv = round(pmv, 3)
                    return pmv
                else:
                    return None
            else:
                return None
        except Exception as e:
            print(e, "In ThermalComfort.thermal_calculation")
            logging.exception(e)
            return None

    def thermal_estimation_ashrae(self, temperature, humidity, timestamp):
        """Estimatates thermal comfort based on ASHRAE tables for the values of 
        clothing insulation  and metabolic rate values.
        return activity
        :param float temperature:  current temperature 
        :param float humidity:  current humidity
        :param Datetime timestamp:
        :param file file: the file that the values for metabolic rate and 
        clothing insulation from the ASHRAE table are saved. The 
        saved values are per 5 predefined time-zones [1-5] and per season.
        :returnfloat:  thermal comfort based on ASHRAE tables [-3,3] 
        """
        try:
            icl_season = self.clothing_by_season(timestamp)
            m_season = self.activity_by_season(timestamp)
            pmv_ashrae_current = self.thermal_calculation(temperature, humidity, icl_season, m_season)
            pmv_ashrae_current = correct_thresholds(pmv_ashrae_current)
            return pmv_ashrae_current
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.thermal_estimation_ashrae")
            return None

    def thermal_estimation_adjust(self, temperature, humidity, timestamp):
        """Estimatates thermal comfort based on adjusted clothing insulation 
        and metabolic rate.
        :param float temperature: current temperature 
        :param float humidity: current humidity
        :param Datetime timestamp:
        :return float:  adjusted thermal comfort [-3,3]
        """
        try:
            icl_adapt = self.clothing_adjustment(temperature, timestamp)
            m_adapt = self.activity_adjustment(temperature, timestamp)
            pmv_adapted = self.thermal_calculation(temperature, humidity, icl_adapt, m_adapt)
            pmv_adapted = correct_thresholds(pmv_adapted)
            return pmv_adapted
        except Exception as e:
            logging.exception(e)
            print(e, "In ThermalComfort.thermal_estimation_adjust")
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
        print(e, "correct_thresholds")
        return None
