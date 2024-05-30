from pathlib import Path
import configparser
# from Recommendation.Savings import Savings
from datetime import datetime as dt, timedelta as delta
import datetime
import logging


class HandleClientConfig:
    """
    Contains all the functions needed to handle the client specific config.ini file.
    """

    def __init__(self,
                 client,
                 date,
                 read_data,
                 reinit_config=False):
        """
        """
        client_data = read_data
        try:
            self.section = "recommendations"
            self.client = client
            self.date = date
            config_path = client_data.get_files(self.client, 'Configs')
            self.recs = {}
            self.refrains = client_data.get_refrains()
            for o in config_path:
                if "config" in o:
                    self.path = Path(o)
                    self.config = configparser.ConfigParser()
                    self.config.read(self.path)
                    self.number_of_recommendations = int(self.config.get(self.section, 'number_of_recommendations'))
                    if reinit_config:
                        self.reinit_config()
                    # self.basic_refrain = int(self.config.get(self.section, 'basic_refrain'))
                    # self.today = str_to_dt(self.config.get(self.section, 'today'))
                    # self.last_sent = str_to_dt(self.config.get(self.section, 'last_sent'))

                    self.heater = {
                        "duration_1": int(self.config.get("heater_averaging", 'duration_1')),
                        "duration_2": int(self.config.get("heater_averaging", 'duration_2')),
                        "duration_3": int(self.config.get("heater_averaging", 'duration_3')),
                        "heater_on": str_to_dt(self.config.get("heater_averaging", 'heater_on')),
                        "heater_is_on": bool(int(self.config.get("heater_averaging", 'heater_is_on')))
                    }

                    for i in range(1, self.number_of_recommendations+1):
                        self.recs[i] = {
                            "message": self.config.get(self.section, 'message' + str(i)),
                            "rate": self.config.get(self.section, 'rate' + str(i)),
                            "sent": self.config.getboolean(self.section, 'sent' + str(i)),
                            "feedback_timer": int(self.config.get(self.section, 'feedback_timer' + str(i))),
                            "acc": self.config.get(self.section, 'acc' + str(i)),
                            "last_sent": self.config.get(self.section, 'last_sent' + str(i)),
                            "refrain": int(self.config.get(self.section, 'refrain' + str(i))),
                        }

                    # self.weekly_consumption = {
                    #     "rate": self.config.getint(self.section, 'g_rate1'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent1')))
                    # }
                    # self.weekly_savings = {
                    #     "rate": self.config.getint(self.section, 'g_rate2'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent2')))
                    # }
                    # self.change_setpoint = {
                    #     "rate": self.config.getint(self.section, 'g_rate3'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent3')))
                    # }
                    # self.turn_off_standby = {
                    #     "rate": self.config.getint(self.section, 'g_rate4'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent4')))
                    # }
                    # self.open_windows = {
                    #     "rate": self.config.getint(self.section, 'g_rate5'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent5')))
                    # }
                    # self.smartplugs = {
                    #     "rate": self.config.getint(self.section, 'g_rate6'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent6')))
                    # }
                    # self.efficient = {
                    #     "rate": self.config.getint(self.section, 'g_rate7'),
                    #     "sent": bool(int(self.config.get(self.section, 'g_sent7')))
                    # }


                    # savings_list = self.check_for_feedback()
                    # self.check_general()

            # self._new_day_week()
        except Exception as e:
            print("Exception in HandleClientConfig.__init__", e)
            logging.exception(e)

    def set_field(self, field, value, section=None):
        """
        Changes the specific 'field' in the client's config.ini file with the 'value' variable
        :param field: Field name
        :param value: New Field Value
        :param section Section else self.section
        """
        try:
            if not section:
                section = self.section
            if type(value) == datetime.datetime:
                value = value.strftime("%Y-%m-%dT%H:%M:%S.000Z")
            else:
                value = str(value)
            self.config.set(section, field, value)
            self.config.write(open(self.path, "w"))
        except Exception as e:
            print("Exception in HandleClientConfig.set_field")
            logging.exception(e)

    def _up_refrain(self, num):
        """
        Uppers the refrain value for this recommendation.
        :param num: Recommendation number identifier
        """
        try:
            current = self.recs[num]["refrain"]
            for k in range(len(self.refrains)):
                if current == self.refrains[k]:
                    if k < len(self.refrains)-1:
                        new = self.refrains[k+1]
                        self.set_field("refrain"+str(num), new)
        except Exception as e:
            print("Exception in HandleClientConfig._up_refrain")
            logging.exception(e)

    def _down_refrain(self, num):
        """
        :param num: Lowers the refrain value for this recommendation.
        :return: Recommendation number identifier
        """
        try:
            current = self.recs[num]["refrain"]
            for k in range(len(self.refrains)):
                if current == self.refrains[k]:
                    if k > 0:
                        new = self.refrains[k-1]
                        self.set_field("refrain"+str(num), new)
        except Exception as e:
            print("Exception in HandleClientConfig._down_refrain")
            logging.exception(e)

    def _check_refrain(self, rec):
        """
        Checks if the same recommendation has been sent to the user within the 'refrain' time.
        If True, discard the new recommendation.
        :param rec: New Recommendation
        :return: rec (Recommendation) if not in refrain time, None else
        """
        try:
            # if not self.limit_exceeded:
            refrains = []
            for i in rec:
                no = i["number"]
                if no < 99:
                    refrain = int(self.recs[no]["refrain"])
                    last_sent = str_to_dt(self.recs[no]["last_sent"])
                    if self.date - last_sent > delta(hours=refrain):
                        refrains.append(i)
                else:
                    refrains.append(i)
            return refrains if refrains else None
        except Exception as e:
            print("Exception in HandleClientConfig._check_refrain ", self.client, rec)
            logging.exception(e)
            return None

    def get_heater_average(self):
        """
        :return: Average duration over the last 3 uses of the client's water heater multiplied by a safety threshold
        """
        return int(((self.heater["duration_1"] + self.heater["duration_2"] + self.heater["duration_3"]) / 3)*1.25)

    def handle_new_recommendations(self, rec):
        """
        Pipeline of checks to define if any of the new recommendations are going to be sent to the user.
        If the recommendations are multiple, keeps the one with the higher priority.
        Finally, if a recommendations is sent to the user, update the user's config.ini
        :param rec: New Recommendations
        :return: rec (Recommendation) if any passes the checks, else None
        """
        try:
            rec = self._check_refrain(rec)
            # if rec:
            #     rec = _keep_best(rec)
            if rec:
                for r in rec:
                    self._set_config_fields_for_new_rec(r)
                return rec
            else:
                return []
        except Exception as e:
            print("Exception in HandleClientConfig.handle_new_recommendations")
            logging.exception(e)
            return None

    def _set_config_fields_for_new_rec(self, rec):
        """
        Updates all the fields in te user's config.ini file, based on the new recommendation
        :param rec: New recommendation
        """
        try:
            no = str(rec["number"])
            s = "sent"+no
            d = "last_sent"+no
            self.set_field(s, True)
            self.set_field(d, self.date)
            self.set_field("last_sent", self.date)
            # self.set_field("day_recs", self.day_recs+1)
            # self.set_field("week_recs", self.week_recs+1)
            if rec["number"] == 6:
                m = "message"+no
                self.set_field(m, rec["message"])
        except Exception as e:
            print("Exception in HandleClientConfig._set_config_fields_for_new_rec")
            logging.exception(e)

    def reinit_config(self):
        """
        Reinitialize the user's config file to the starting values specified below
        """
        try:
            # self.config.set(self.section, "today", "2020-12-01T00:00:00.000Z")
            # self.config.set(self.section, "last_sent", "2019-12-01T00:00:00.000Z")
            # self.config.set(self.section, "day_recs", "0")
            # self.config.set(self.section, "week_recs", "0")
            self.config.set("heater_averaging", "heater_is_on", "0")
            self.config.set("heater_averaging", "duration_1", "48")
            self.config.set("heater_averaging", "duration_2", "48")
            self.config.set("heater_averaging", "duration_3", "48")
            self.config.set("heater_averaging", "heater_on", "2020-03-10T18:01:00.000Z")
            for r in range(1, self.number_of_recommendations+1):
                self.config.set(self.section, "refrain"+str(r), "3")
                self.config.set(self.section, "last_sent"+str(r), "2019-12-01T00:00:00.000Z")
                self.config.set(self.section, "sent"+str(r), "False")

            # for g in range(1, self.number_of_general):
            #     self.config.set(self.section, "g_sent"+str(g), "0")
            # self.config.set(self.section, "g_rate5", "1")

            self.config.write(open(self.path, "w"))
        except Exception as e:
            print("Exception in HandleClientConfig.reinit_config")
            logging.exception(e)

    # def check_general(self):
    #     """
    #     Check the current date and search for general
    #     recommendations if it matches the preferred time window
    #     """
    #     # GENERAL 1
    #     if self.date.weekday() == 6 and self.date.hour == 17 and self.weekly_consumption["sent"]:
    #         self.set_field("g_sent1", "0")
    #     # GENERAL 2
    #     if self.date.weekday() == 6 and self.date.hour == 11 and self.weekly_savings["sent"]:
    #         self.set_field("g_sent2", "0")
    #     # GENERAL 3
    #     if self.date.weekday() == 5 and self.date.hour == 11 and self.change_setpoint["sent"]:
    #         self.set_field("g_sent3", "0")
    #     # GENERAL 4
    #     if self.date.weekday() == 5 and self.date.hour == 17 and self.turn_off_standby["sent"]:
    #         self.set_field("g_sent4", "0")
    #     # GENERAL 5
    #     if self.date.weekday() == 0 and self.date.hour == 17 and self.open_windows["sent"]:
    #         self.set_field("g_sent5", "0")
    #     # GENERAL 6
    #     if self.date.weekday() == 1 and self.date.hour == 17 and self.smartplugs["sent"]:
    #         self.set_field("g_sent6", "0")

    # def _limits(self):
    #     """
    #     Function checking if any of the recommendation limits are exceeded.
    #     :return: True if any of the limits are exceeded, in which cases any new recommendation is going to be discarded.
    #     """
    #     try:
    #         if self.day_recs >= self.max_per_day:
    #             return True
    #         if self.week_recs >= self.max_per_week:
    #             return True
    #         if self.date - self.last_sent < delta(hours=self.basic_refrain):
    #             return True
    #         return False
    #     except Exception as e:
    #         print("Exception in HandleClientConfig._limits")
    #         logging.exception(e)

    # def _new_day_week(self):
    #     """
    #     Sets the daily recommendation counter to zero, each day
    #     Sets the weekly recommendation counter to zero, each week (Monday)
    #     """
    #     try:
    #         if self.date.day != self.today.day:
    #             self.set_field("today", self.date)
    #             self.set_field("day_recs", 0)
    #             if self.date.weekday() == 0:
    #                 self.set_field("week_recs", 0)
    #     except Exception as e:
    #         print("Exception in HandleClientConfig._new_day_week")
    #         logging.exception(e)

    # def check_for_feedback(self):
    #     """
    #     Checks for feedback on any outgoing recommendations.
    #     The amount of time for which the module checks for feedback is defined in the clients config.ini file.
    #     Changes the time to refrain from sending the same recommendation, based on feedback.
    #     Calls the Savings class to calculate the Savings from each recommendation, if possible.
    #     """
    #     try:
    #         savings_matrix = []
    #         savings_matrix.append("check for feedback")
    #         for j in range(1, self.number_of_recommendations+1):
    #             e = self.recs[j]
    #             last_sent = str_to_dt(e["last_sent"])
    #             savings_matrix.append(f"last_sent {last_sent}")
    #             savings_matrix.append(f"sent {e['sent']}")
    #             if e["sent"]:
    #                 savings_matrix.append(f"e sent {e}")
    #                 if (self.date - last_sent) > delta(minutes=e["feedback_timer"]):
    #                     savings_matrix.append("checking for actual savings")
    #                     savings = Savings(self.path, self.client, e["message"], j, last_sent, nowdate=self.date)
    #                     temp = savings.get_savings()
    #                     savings_matrix.append(f"result: {temp}")
    #                     if temp is not None:
    #                         savings_matrix.append(temp)
    #                     self.set_field("sent"+str(j), False)
    #                     self._up_refrain(j)
    #                 else:
    #                     savings = Savings(self.path,
    #                                       self.client,
    #                                       e["message"],
    #                                       j,
    #                                       last_sent,
    #                                       nowdate=self.date,
    #                                       active=True)
    #                     # TODO FIX NEEDS DATA
    #                     f = savings.search_for_feedback([0, 0, 0, 0, 0, 0])
    #                     savings_matrix.append("search for feedback")
    #                     if f:
    #                         temp = savings.get_savings()
    #                         if temp is not None:
    #                             savings_matrix.append("checking for potential savings")
    #                             self.set_field("sent" + str(j), False)
    #                             if savings["Type"] == "passive":
    #                                 self._up_refrain(j)
    #                             else:
    #                                 self._down_refrain(j)
    #         savings_matrix.append(f"returning savings: {savings_matrix}")
    #         return savings_matrix
    #     except Exception as e:
    #         print("Exception in HandleClientConfig.check_for_feedback", e)
    #         logging.exception(e)


# def _keep_best(rec):
#     """
#     Keeps the best of multiple recommendations based on their priorities
#     :param rec: List of new recommendations
#     :return: Higher priority recommendation
#     """
#     try:
#         best = None
#         if len(rec) > 0:
#             best = rec[0]
#         if len(rec) > 1:
#             for i in range(1, len(rec)):
#                 if rec[i]['rate'] > best['rate']:
#                     best = rec[i]
#         return best
#     except Exception as e:
#         print("Exception in HandleClientConfig._keep_best, ")
#         logging.exception(e)
#         return None


def str_to_dt(st):
    """
    Convert a String object to datetime
    :param st: String timestamp object
    :return: Datetime timestamp object
    """
    try:
        return dt.strptime(st, "%Y-%m-%dT%H:%M:%S.000Z")
    except Exception as e:
        print("Exception in HandleClientConfig.str_to_dt, ")
        logging.exception(e)
        return None


def dt_to_str(dat):
    """
    Convert a Datetime object to String
    :param dat: Datetime timestamp object
    :return: String timestamp object
    """
    try:
        return dat.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    except Exception as e:
        print("Exception in HandleClientConfig.dt_to_str")
        logging.exception(e)
        return None
