import logging
import os
import sys
from datetime import datetime as dt, timedelta as delta


# Disable
def block_print():
    sys.stdout = open(os.devnull, 'w')


# Restore
def enable_print():
    sys.stdout = sys.__stdout__


class Savings:
    """This is the savings module's entry Class.
    Uses recommendations and sensor data as input
    to calculate a recommendation's real or
    hypothetical savings.
    """

    def __init__(self, args):
        """
        """
        try:
            block_print()
            self.active_timer = 15
            self.feedback_limit = 120
            self.client = args["client"]
            self.timestamp = str_to_dt(args["timestamp"])
            self.number = args["number"]
            self.sent_at = str_to_dt(args["sent_at"])
            self.power_interval = args["power_interval"]
            self.power = args["power"]
            self.power_before = []
            self.power_after = []
            self.data_len = len(self.power)
            if self.number in [9, 10, 11, 12, 13, 14, 15, 16]:
                self.setTemp = args["setTemp"]
            # Thermostat consumption in wh per hour
            self.thermostat_avg_kwh = 20000
            # Hvac consumption in wh per hour
            self.hvac_avg_kwh = 1200
            # percentage of energy saved per 1 Celsius difference in setTemp
            self.percentage_per_celsius = 6 / 100
        except Exception as e:
            print("Exception in Savings.__init__")
            logging.exception(e)

    def check_data_window(self, cutoff_low_powers=False):
        """
        Compares the timestamps of the incoming data
        to the recommendation timestamp and splits into windows
        for data before and after the recommendation
        """
        for p in range(self.data_len):
            self.power[p][0] = str_to_dt(self.power[p][0])

        for p in range(self.data_len):
            if delta(minutes=0) <= self.power[p][0] - self.sent_at < delta(minutes=self.feedback_limit):
                if cutoff_low_powers and self.power[p][1] < 5:
                    self.power_after.append([self.power[p][0], 0])
                else:
                    self.power_after.append(self.power[p])
            if delta(minutes=-30) <= self.power[p][0] - self.sent_at < delta(minutes=0):
                if cutoff_low_powers and self.power[p][1] < 5:
                    self.power_before.append([self.power[p][0], 0])
                else:
                    self.power_before.append(self.power[p])

    def get_savings(self):
        """
        Calls the appropriate function to calculate the savings
        and posts the savings to the platform using the Api class
        """
        savings = None
        feedback = None
        try:
            if self.number in [1, 4, 5, 6]:
                self.check_data_window(cutoff_low_powers=True)
                savings, feedback = self._get_savings_devices()
            elif self.number in [9, 10, 13, 14]:
                self.check_data_window()
                savings, feedback = self._get_savings_hvac()
            elif self.number in [11, 12, 15, 16]:
                self.check_data_window()
                savings, feedback = self._get_savings_thermostat()
            if savings is not None:
                if type(savings) is str:
                    return {
                        "number": self.number,
                        "sent_at": dt_to_str(self.sent_at),
                        "error": savings
                    }
                else:
                    return {
                        "number": self.number,
                        "sent_at": dt_to_str(self.sent_at),
                        "type": feedback,
                        "savings": float(savings)
                    }
            else:
                return {
                    "number": self.number,
                    "sent_at": dt_to_str(self.sent_at),
                    "error": f"Savings cannot be calculated for recommendation No.{self.number}"
                }
        except Exception as e:
            print("Exception in Savings.calculate")
            logging.exception(e)
        return savings if savings is not None else None

    def _get_savings_devices(self):
        """
        """
        try:
            feedback, timer = self.search_for_feedback()
            if feedback is not None:
                if feedback == -1:
                    return timer, None
                elif feedback == 1:
                    wh = self._get_wh_active(timer)
                else:
                    wh = self._get_wh_passive(timer)
                return wh, feedback
            else:
                return None, None
        except Exception as e:
            print("Exception in Savings._get_savings_1")
            logging.exception(e)
            return None, None

    def search_for_feedback(self):
        """
        Searches for feedback for this instance's recommendation
        :return: boolean True if feedback is found
        """
        try:
            if self.power_after is not None:
                data_len = len(self.power_after)
                for i in range(data_len - 1):
                    if self.power_after[i][1] == 0:
                        flag = True
                        counter = 1
                        for j in range(i + 1, data_len, 1):
                            if self.power_after[j][1] != 0:
                                flag = False
                                break
                            else:
                                counter += 1
                                if counter == 30:
                                    break
                        if flag:
                            if i <= self.active_timer / self.power_interval:
                                return 1, i
                            else:
                                return 0, i
                return 0, data_len - 1
            else:
                return -1, "Not enough data to calculate savings."
        except Exception as e:
            print("Exception in Savings.search_for_feedback")
            logging.exception(e)
            return None, None

    def _get_wh_active(self, timer):
        """
        """
        try:
            power_before = self.power_before + self.power_after[:timer]
            watt_before = 0

            if not power_before:
                return "Cannot calculate average power"

            tms_counter = 0
            for i in range(len(power_before)):
                pwr = power_before[i][1]
                if pwr != 0:
                    tms_counter += 1
                    watt_before += power_before[i][1]
            if tms_counter != 0:
                avg_watt = watt_before / tms_counter
            else:
                avg_watt = 0

            savings = (len(self.power_after) - timer) * avg_watt * self.power_interval / 60

            return round(savings, 2)
        except Exception as e:
            print("Exception in Savings._get_wh")
            logging.exception(e)
            return None

    def _get_wh_passive(self, timer):
        """
        """
        try:
            savings = 0
            for i in range(timer):
                savings += self.power_after[i][1] * self.power_interval / 60
            return round(savings, 2)
        except Exception as e:
            print("Exception in Savings._get_wh")
            logging.exception(e)
            return None

    def _get_savings_hvac(self):
        """
        on/off: 0 off, 1,2,3, on
        """
        try:
            feedback, timer = self.search_for_feedback_hvac_thermo()
            print(f"feedback {feedback}, timer {timer}")
            if feedback is not None:
                if feedback == -1:
                    return timer, None
                elif feedback == 1:
                    wh = self._get_hvac_thermo_active(timer)
                else:
                    wh = self._get_hvac_thermo_passive(timer)
                return wh, feedback
            else:
                return None, None
        except Exception as e:
            print("Exception in Savings._get_savings_1")
            logging.exception(e)
            return None, None

    def _get_savings_thermostat(self):
        """
        on/off: 0 off, 1 on
        """
        try:
            feedback, timer = self.search_for_feedback_hvac_thermo()
            print(f"feedback {feedback}, timer {timer}")
            if feedback is not None:
                if feedback == -1:
                    return timer, None
                elif feedback == 1:
                    wh = self._get_hvac_thermo_active(timer, is_thermo=True)
                else:
                    wh = self._get_hvac_thermo_passive(timer, is_thermo=True)
                return wh, feedback
            else:
                return None, None
        except Exception as e:
            print("Exception in Savings._get_savings_1")
            logging.exception(e)
            return None, None

    def search_for_feedback_hvac_thermo(self):
        """
        Searches for feedback for this instance's recommendation
        :return: boolean True if feedback is found
        """
        try:
            if self.power_after:
                data_len = len(self.power_after)
                if self.number == 9 or self.number == 14 or self.number == 11 or self.number == 16:
                    for i in range(data_len - 1):
                        if self.power_after[i][1] <= self.setTemp or self.power_after[i][2] == 0:
                            flag = True
                            counter = 1
                            for j in range(i + 1, data_len, 1):
                                if self.power_after[j][2] != 0 and self.power_after[j][1] > self.setTemp:
                                    flag = False
                                    break
                                else:
                                    counter += 1
                                    if counter == 30:
                                        break
                            if flag:
                                if i <= self.active_timer / self.power_interval:
                                    return 1, i
                                else:
                                    return 0, i
                    return 0, data_len - 1
                elif self.number == 10 or self.number == 13 or self.number == 12 or self.number == 15:
                    for i in range(data_len - 1):
                        if self.power_after[i][1] >= self.setTemp or self.power_after[i][2] == 0:
                            flag = True
                            counter = 1
                            for j in range(i + 1, data_len, 1):
                                if self.power_after[j][2] != 0 and self.power_after[j][1] < self.setTemp:
                                    flag = False
                                    break
                                else:
                                    counter += 1
                                    if counter == 30:
                                        break
                            if flag:
                                if i <= self.active_timer / self.power_interval:
                                    return 1, i
                                else:
                                    return 0, i
                    return 0, data_len - 1
                else:
                    pass
            else:
                return -1, "Not enough data to calculate savings."
        except Exception as e:
            print("Exception in Savings.search_for_feedback")
            logging.exception(e)
            return None, None

    def _get_hvac_thermo_active(self, timer, is_thermo=False):
        """
        """
        try:
            power_before = self.power_before + self.power_after[:timer]
            before_len = len(power_before)
            if not power_before:
                return "Cannot calculate setTemp before action"
            hours = (len(self.power_after) - timer) / 60
            set_temps = 0
            for i in range(before_len):
                set_temp = power_before[i][1]
                set_temps += set_temp

            if is_thermo:
                set_before = round((set_temps / before_len)*2)/2
            else:
                set_before = round(set_temps / before_len)

            temp = 0
            for i in range(timer, timer + 30, 1):
                temp += self.power_after[i][1]

            if is_thermo:
                actual_set_temp = round((temp / 30)*2)/2
            else:
                actual_set_temp = round(temp / 30)

            if self.number == 9 or self.number == 11 or self.number == 14 or self.number == 16:
                if set_before <= self.setTemp:
                    print("Hvac was already in the suggested")
                if actual_set_temp <= self.setTemp:
                    actual_set_temp = self.setTemp
                    actual_diff = set_before - actual_set_temp
                    savings = 0
                    if self.number == 9:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 14:
                        savings = hours * 1 * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 11:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.thermostat_avg_kwh
                    elif self.number == 16:
                        savings = hours * 0.5 * self.percentage_per_celsius * self.thermostat_avg_kwh
                    return round(savings, 2)
                elif self.setTemp < actual_set_temp < set_before:
                    # TODO Calculate half passive half active
                    actual_diff = set_before - actual_set_temp
                    savings = 0
                    if self.number == 9:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 14:
                        savings = hours * 1 * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 11:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.thermostat_avg_kwh
                    elif self.number == 16:
                        savings = hours * 0.5 * self.percentage_per_celsius * self.thermostat_avg_kwh
                    return round(savings, 2)
                else:
                    return 0
            elif self.number == 10 or self.number == 12 or self.number == 13 or self.number == 15:
                if set_before >= self.setTemp:
                    print("Hvac was already in the suggested")
                if actual_set_temp >= self.setTemp:
                    actual_set_temp = self.setTemp
                    actual_diff = actual_set_temp - set_before
                    savings = 0
                    if self.number == 10:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 13:
                        savings = hours * 1 * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 12:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.thermostat_avg_kwh
                    elif self.number == 15:
                        savings = hours * 0.5 * self.percentage_per_celsius * self.thermostat_avg_kwh
                    return round(savings, 2)
                elif set_before < actual_set_temp < self.setTemp:
                    # TODO Calculate half passive half active
                    actual_diff = actual_set_temp - set_before
                    savings = 0
                    if self.number == 10:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 13:
                        savings = hours * 1 * self.percentage_per_celsius * self.hvac_avg_kwh
                    elif self.number == 12:
                        savings = hours * actual_diff * self.percentage_per_celsius * self.thermostat_avg_kwh
                    elif self.number == 15:
                        savings = hours * 0.5 * self.percentage_per_celsius * self.thermostat_avg_kwh
                    return round(savings, 2)
                else:
                    return 0
            else:
                print("self.number out of function bounds")
        except Exception as e:
            print("Exception in Savings._get_wh")
            logging.exception(e)
            return None

    def _get_hvac_thermo_passive(self, timer, is_thermo=False):
        """
        """
        try:
            hours = (len(self.power_after) - timer) / 60

            power_before = self.power_before + self.power_after[:timer]
            before_len = len(power_before)
            set_temps = 0
            for i in range(before_len):
                set_temp = power_before[i][1]
                set_temps += set_temp

            if is_thermo:
                set_before = round((set_temps / before_len)*2)/2
            else:
                set_before = round(set_temps / before_len)

            diff = abs(set_before - self.setTemp)

            savings = 0

            if self.number == 10 or self.number == 9:
                savings = hours * diff * self.percentage_per_celsius * self.hvac_avg_kwh
            elif self.number == 13 or self.number == 14:
                savings = hours * 1 * self.percentage_per_celsius * self.hvac_avg_kwh
            elif self.number == 12 or self.number == 11:
                savings = hours * diff * self.percentage_per_celsius * self.thermostat_avg_kwh
            elif self.number == 15 or self.number == 16:
                savings = hours * 0.5 * self.percentage_per_celsius * self.thermostat_avg_kwh

            return round(savings, 2)
        except Exception as e:
            print("Exception in Savings._get_wh")
            logging.exception(e)
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
        print("Exception in Savings.str_to_dt")
        logging.exception(e)



def dt_to_str(dat):
    try:
        return dat.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Exception in Tools.dt_to_str")
        logging.exception(e)
        return None
