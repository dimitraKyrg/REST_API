from Recommendation.HandleClientConfig import HandleClientConfig
import pickle
import logging
from Recommendation.VisualComfortLights import VisualComfortLights
from Recommendation.ThermalComfortHvac import ThermalComfortHvac
from Recommendation.ThermalComfortThermostat import ThermalComfortThermostat
import json
from datetime import datetime as dt, timedelta as delta
import warnings

warnings.filterwarnings("ignore")


class Recommend:
    """
    This Class:
    1. Compares model predictions with real time sensor data
    2. Checks for working devices if house is
        unoccupied for a defined time window.
    3. Checks for devices that function longer than usual.
        (example: Water Heater is ON for 2 hours.)
    4. Calculates recommendations based on all previous checks
        and returns them to the Recommendation class for further
        processing.

    Recommendation List:
    1. Water Heater on for over an {interval}
    2. Humidity inside the house can be lowered by opening the windows.
    3. Co2 inside the house can be lowered by opening the windows.
    4. Turn off the HVAC
    5. Turn off the Lights
    6. Turn off the {device}
    7. Washing Machine saves energy if activated at night
    8. Lower the dimmer of the Lights to {%}
    9. Lower HVAC temperature to {degrees}
    10. Upper HVAC temperature to {degrees}
    11. Lower thermostat temperature to {degrees}
    12. Upper thermostat temperature to {degrees}
    13. You could try changing HVAC temperature by +1 C to save energy.
    14. You could try changing HVAC temperature by -1 C to save energy.
    15. You could try changing thermostat temperature by +0.5 C to save energy.
    16. You could try changing thermostat temperature by -0.5 C to save energy.

    101. This week your consumption was 4.69 kWh, 6.7% more compared to last week.
    102. This week's recommendations resulted in actual savings of 8.96 kWh.
        If all the recommended actions were followed, they could result in an
        extra 2.73 kWh of savings.
    103. You could try changing your heating unit's set point by 1 degree.
        This will lower the unit's consumption by an average of 6%.
    104. Remember to turn off standby devices.
    105. Remember to open the windows when the weather is good, to lower
        the humidity inside the house.
    106. This week the following plugs had unusually high consumption
        compared to last week: plug_name_1 up by 3.23 kWh
    107. You could use a more efficient heating solution.
    """

    def __init__(self, data, read_data, language='GR'):
        """
        :param json [] data: Object Initialization Input Matrix.
        :param Object read_data: ReadData class instance
        """
        self.language = language
        if self.language == 'GR':
            self.r1, self.r1_rate, self.no1 = "Water Heater on for over ", 2, 1
            self.r2, self.r2_rate, self.no2 = "Humidity inside the house can be lowered by opening the windows.", 0, 2
            self.r3, self.r3_rate, self.no3 = "Co2 inside the house can be lowered by opening the windows.", 0, 3
            self.r4, self.r4_rate, self.no4 = "Turn off the HVAC", 2, 4
            self.r5, self.r5_rate, self.no5 = "Turn off the Lights", 0, 5
            self.r6, self.r6_rate, self.no6 = "Turn off the", 1, 6
            self.r7, self.r7_rate, self.no7 = "Washing Machine saves energy if activated at night", 1, 7
            self.r8, self.r8_rate, self.no8 = "Lower the dimmer of the Lights to", 0, 8
            self.r9, self.r9_rate, self.no9 = "Lower HVAC temperature to", 1, 9
            self.r10, self.r10_rate, self.no10 = "Upper HVAC temperature to", 1, 10
            self.r11, self.r11_rate, self.no11 = "Lower thermostat temperature to", 1, 11
            self.r12, self.r12_rate, self.no12 = "Upper thermostat temperature to", 1, 12
            self.r13, self.r13_rate, self.no13 = "You could try changing HVAC temperature by +1 C to save energy.", 1, 13
            self.r14, self.r14_rate, self.no14 = "You could try changing HVAC temperature by -1 C to save energy.", 1, 14
            self.r15, self.r15_rate, self.no15 = "You could try changing thermostat temperature by +0.5 C to save energy.", 1, 15
            self.r16, self.r16_rate, self.no16 = "You could try changing thermostat temperature by -0.5 C to save energy.", 1, 16

            self.r101, self.r101_rate, self.no101 = "Αυτή την εβδομάδα η κατανάλωσή σου ήταν {power} kWh, {percent}% {περισσότερο/λιγότερο} από την προηγούμενη εβδομάδα.", 2, 101
            self.r102, self.r102_rate, self.no102 = "This week's recommendations resulted in actual savings of {power} kWh. If all the recommended actions were followed, they could result in an extra {extra} kWh of savings.", 2, 102
            self.r103, self.r103_rate, self.no103 = "Δοκίμασε να αλλάξεις τη θερμοκρασία στο σύστημα θέρμανσής σου κάτα ένα βαθμό και εξοικονόμησε έως 6%.", 2, 103
            self.r104, self.r104_rate, self.no104 = "Θυμίσου να απενεργοποιείς εντελώς τις συσκευές, όταν δεν χρησιμοποιούνται.", 2, 104
            self.r105, self.r105_rate, self.no105 = "Smart Tip! Μπορείς να μειώσεις την υγρασία στο σπίτι ανοίγοντας τα παράθυρα όταν έχει καλό καιρό.", 2, 105
            self.r106, self.r106_rate, self.no106 = "Αυτή την εβδομάδα οι παρακάτω πρίζες είχαν ασυνήθιστα υψηλή κατανάλωση σε σχέση με την προηγούμενη εβδομάδα: {plug_name_1}: {power} kWh παραπάνω", 2, 106
            self.r107, self.r107_rate, self.no107 = "Χρησιμοποίησε πιο αποδοτικά συστήματα θέρμανσης για να εξοικονομήσεις περισσότερη ενέργεια.", 2, 107

        else:
            self.r1, self.r1_rate, self.no1 = "Water Heater on for over ", 2, 1
            self.r2, self.r2_rate, self.no2 = "Humidity inside the house can be lowered by opening the windows.", 0, 2
            self.r3, self.r3_rate, self.no3 = "Co2 inside the house can be lowered by opening the windows.", 0, 3
            self.r4, self.r4_rate, self.no4 = "Turn off the HVAC", 2, 4
            self.r5, self.r5_rate, self.no5 = "Turn off the Lights", 0, 5
            self.r6, self.r6_rate, self.no6 = "Turn off the", 1, 6
            self.r7, self.r7_rate, self.no7 = "Washing Machine saves energy if activated at night", 1, 7
            self.r8, self.r8_rate, self.no8 = "Lower the dimmer of the Lights to", 0, 8
            self.r9, self.r9_rate, self.no9 = "Lower HVAC temperature to", 1, 9
            self.r10, self.r10_rate, self.no10 = "Upper HVAC temperature to", 1, 10
            self.r11, self.r11_rate, self.no11 = "Lower thermostat temperature to", 1, 11
            self.r12, self.r12_rate, self.no12 = "Upper thermostat temperature to", 1, 12
            self.r13, self.r13_rate, self.no13 = "You could try changing HVAC temperature by +1 C to save energy.", 1, 13
            self.r14, self.r14_rate, self.no14 = "You could try changing HVAC temperature by -1 C to save energy.", 1, 14
            self.r15, self.r15_rate, self.no15 = "You could try changing thermostat temperature by +0.5 C to save " \
                                                 "energy.", 1, 15
            self.r16, self.r16_rate, self.no16 = "You could try changing thermostat temperature by -0.5 C to save " \
                                                 "energy.", 1, 16

            self.r101, self.r101_rate, self.no101 = "This week your consumption was {power} kWh, {percent}% {" \
                                                    "more/less} compared to last week.", 2, 101
            self.r102, self.r102_rate, self.no102 = "This week's recommendations resulted in actual savings of {" \
                                                    "power} kWh. If all the recommended actions were followed, " \
                                                    "they could result in an extra {extra} kWh of savings.", 2, 102
            self.r103, self.r103_rate, self.no103 = "You could try changing your heating unit's set point by 1 " \
                                                    "degree. This will lower the unit's consumption by an average of " \
                                                    "6%.", 2, 103
            self.r104, self.r104_rate, self.no104 = "Remember to turn off standby devices.", 2, 104
            self.r105, self.r105_rate, self.no105 = "Remember to open the windows when the weather is good, to lower " \
                                                    "the humidity inside the house.", 2, 105
            self.r106, self.r106_rate, self.no106 = "This week the following plugs had unusually high consumption " \
                                                    "compared to last week: {plug_name_1} up by {power} kWh", 2, 106
            self.r107, self.r107_rate, self.no107 = "You could use a more efficient heating solution.", 2, 107

        try:
            self.d = data
            self.read_data = read_data
            self.validity_json = {}
            self.client = self.check_none(self.d['client'], "str")
            self.train = self.check_none(self.d['train'], "bool")
            self.date = self.check_none(self.d['timestamp'], "timestamp")
            self.config_ops = HandleClientConfig(self.client,
                                                 self.date,
                                                 self.read_data,
                                                 reinit_config=self.d["reinitialize_recommendations"])
            self.recs = []
            # self.savings = self.config_ops.check_for_feedback()
            # files
            if self.key_in_json('files'):
                files = self.d['files']
                self.thermal_model_AC = self.check_none(files['thermal_model_AC'], "str")
                self.thermal_model_thermostat = self.check_none(files['thermal_model_thermostat'], "str")
                self.visual_model = self.check_none(files['visualModel'], "str")
            self.devices = self.check_none(self.d['devices'], "")
            self.occ_60, self.occ_90 = self.check_none(self.d['occupancy'], "occupancy")
            self.night_power_discount = self.check_none(self.d['night_power_discount'], "bool")
            self.co2_thresh = self.check_none(self.d["co2_threshold"], "int")
            self.hum_thresh = self.check_none(self.d['humidity_threshold'], "int")
            if self.key_in_json('indoorConditions'):
                indoor = self.d['indoorConditions']
                self.tem = self.check_none(indoor['temperature'], "float")
                self.hum = self.check_none(indoor['humidity'], "int")
                self.lum = self.check_none(indoor['luminance'], "int")
                self.co2 = self.check_none(indoor["co2"], "int")
            else:
                self.tem = None
                self.hum = None
                self.lum = None
                self.co2 = None
            if self.key_in_json('comfort'):
                self.comfort = self.check_none(self.d['comfort'], "comfort")
            else:
                self.comfort = None
            if self.key_in_json('weather'):
                weather = self.d['weather']
                self.out_tmp = self.check_none(weather['temperature'], "float")
                self.out_hum = self.check_none(weather['humidity'], "int")
                self.ghi = self.check_none(weather['ghi'], "int")
            if self.key_in_json('hvac'):
                hvac = self.d['hvac']
                self.hvac_settemp = self.check_none(hvac['set_temp'], "float")
                self.hvac_status = self.check_none(hvac['status'], "float")
            else:
                self.hvac_settemp = None
                self.hvac_status = None
            if self.key_in_json('thermostat'):
                thermostat = self.d['thermostat']
                self.thermostat_settemp = self.check_none(thermostat['set_temp'], "float")
                self.thermostat_status = self.check_none(thermostat['status'], "float")
            else:
                self.thermostat_settemp = None
                self.thermostat_status = None
            if self.key_in_json('lighting'):
                self.lights = self.d['lighting']
                for key in self.lights.keys():
                    self.lights[key]["dimmer"] = self.check_none(self.lights[key]["dimmer"], "int")
                    self.lights[key]["status"] = self.check_none(self.lights[key]["status"], "int")
                    self.lights[key]["luminance"] = self.check_none(self.lights[key]["luminance"], "int")
                    self.lights[key]["visual_comfort"] = self.check_none(self.lights[key]["visual_comfort"], "float")
            else:
                self.lights = None

            # GENERIC
            if self.key_in_json("generic_turn_off_standby"):
                self.generic_turn_off_standby = self.d["generic_turn_off_standby"]
            else:
                self.generic_turn_off_standby = False
            if self.key_in_json("generic_open_windows"):
                self.generic_open_windows = self.d["generic_open_windows"]
            else:
                self.generic_open_windows = False
            if self.key_in_json("generic_change_setpoint"):
                self.generic_change_setpoint = self.d["generic_change_setpoint"]
            else:
                self.generic_change_setpoint = False
            if self.key_in_json("generic_efficient_heating"):
                self.generic_efficient_heating = self.d["generic_efficient_heating"]
            else:
                self.generic_efficient_heating = False
            if self.key_in_json("generic_upper_thermostat"):
                self.generic_upper_thermostat = self.d["generic_upper_thermostat"]
            else:
                self.generic_upper_thermostat = False
            if self.key_in_json("generic_lower_thermostat"):
                self.generic_lower_thermostat = self.d["generic_lower_thermostat"]
            else:
                self.generic_lower_thermostat = False
            if self.key_in_json("generic_upper_hvac"):
                self.generic_upper_hvac = self.d["generic_upper_hvac"]
            else:
                self.generic_upper_hvac = False
            if self.key_in_json("generic_lower_hvac"):
                self.generic_lower_hvac = self.d["generic_lower_hvac"]
            else:
                self.generic_lower_hvac = False

            if self.key_in_json("water_heater"):
                self.water_heater = self.check_none(self.d["water_heater"], "water_heater")
            else:
                self.water_heater = None
            if self.key_in_json("water_heater_threshold"):
                self.water_heater_threshold = self.check_none(self.d["water_heater_threshold"], int)
        except Exception as e:
            print("Exception in Recommend.__init__")
            logging.exception(e)

    def get_recommendation(self):
        """
        Call this function on a Recommendation Object.
        Calculates new recommendations based on the latest data.

        :return: (String []) contains new recommendations if any are found.

        Return Example:
        [ {'message': "Turn off the Lights"},
        {'message': "Lower the HVAC temperature to 26 C"} ]
        """
        response = []
        try:
            self.validity_json = self.validate_data()
            response = self.search_and_recommend()
        except Exception as e:
            logging.exception(e)
            pass
        return response if response else {}

    # def get_savings(self):
    #     return self.savings

    @staticmethod
    def check_none(key, type_):
        """
        Checks if the key is None.
        If key is None returns None
        else returns the key with proper type
        defined by type_
        :param key: key to be returned
        :param type_: type of the key
        """
        try:
            if key is None or key == {}:
                return None
            else:
                if type_ is "str":
                    return str(key)
                elif type_ is "int":
                    return int(key)
                elif type_ is "bool":
                    return bool(key)
                elif type_ is "float":
                    return round(float(key), 2)
                elif type_ is "timestamp":
                    return str_to_dt(key)
                elif type_ is "occupancy":
                    if (key["60"] == [] or key["60"] is None) and (key["60-90"] == [] or key["60-90"] is None):
                        return None, None
                    occ_60 = False
                    occ_90 = False
                    if ((key["60"].count(0) * 100 / len(key["60"])) > 90) and key["60"][-1] == 0:
                        occ_60 = True
                        mixed_matrix = key["60"] + key["60-90"]
                        if ((mixed_matrix.count(0) * 100 / len(mixed_matrix)) > 90) and mixed_matrix[-1] == 0:
                            occ_90 = True
                    return occ_60, occ_90
                elif type_ is "comfort":
                    if len(key.keys()) > 0:
                        empty = True
                        for k in key.keys():
                            if key[k]["thermal_comfort"] is not None or key[k]["visual_comfort"] is not None:
                                empty = False
                        if empty:
                            return None
                        else:
                            return key
                    else:
                        return None
                elif type_ is "water_heater":
                    for dev, data in key.items():
                        if len(data) < 40:
                            key[dev] = None
                    return key
                else:
                    return key
        except Exception as e:
            print("Exception in Recommend.check_none")
            logging.exception(e)

    def validate_data(self):
        """
        """
        try:
            response = {
                "indoor": True,
                "comforts": False,
                "outdoor": True,
                "hvac": True,
                "thermostat": True,
                "lights": True,
                "water_heater": True
            }
            if self.tem:
                if self.tem is not None:
                    if not (-15 < self.tem < 44):
                        self.tem = None
                        response["indoor"] = False
                else:
                    response["indoor"] = False
            else:
                response["indoor"] = False
            if self.hum:
                if self.hum is not None:
                    if not (0 <= self.hum <= 100):
                        self.hum = None
                        response["indoor"] = False
                else:
                    response["indoor"] = False
            else:
                response["indoor"] = False
            if self.lum:
                if self.lum is not None:
                    if not (0 <= self.lum < 30000):
                        self.lum = None
                        response["indoor"] = False
                else:
                    response["indoor"] = False
            else:
                response["indoor"] = False
            if self.comfort:
                for key in self.comfort.keys():
                    if self.comfort[key]["thermal_comfort"] is not None:
                        if not (-3 <= int(self.comfort[key]["thermal_comfort"]) <= 3):
                            self.comfort[key]["thermal_comfort"] = None
                        else:
                            response["comforts"] = True
                    if self.comfort[key]["visual_comfort"] is not None:
                        if not (-3 <= int(self.comfort[key]["visual_comfort"]) <= 3):
                            self.comfort[key]["visual_comfort"] = None
                        else:
                            response["comforts"] = True
            if self.out_tmp is not None:
                if not (-15 < self.out_tmp < 44):
                    self.out_tmp = None
                    response["outdoor"] = False
            else:
                response["outdoor"] = False
            if self.out_hum is not None:
                if not (0 <= self.out_hum <= 100):
                    self.out_hum = None
                    response["outdoor"] = False
            else:
                response["outdoor"] = False
            if self.ghi is not None:
                if not (0 <= self.ghi <= 20000):
                    self.ghi = None
                    response["outdoor"] = False
            else:
                response["outdoor"] = False

            if self.thermostat_settemp:
                if self.thermostat_settemp is not None:
                    if not (10 <= self.thermostat_settemp <= 40):
                        self.thermostat_settemp = None
                        response["thermostat"] = False
                else:
                    response["thermostat"] = False
            else:
                response["thermostat"] = False
            if self.hvac_settemp:
                if self.hvac_settemp is not None:
                    if not (10 <= self.hvac_settemp <= 40):
                        self.hvac_settemp = None
                        response["hvac"] = False
                else:
                    response["hvac"] = False
            else:
                response["hvac"] = False
            if self.lights:
                if self.lights is not None:
                    for key in self.lights.keys():
                        if not (0 <= self.lights[key]["dimmer"] <= 100):
                            self.lights[key]["dimmer"] = None
                            response["lights"] = False
            if self.water_heater:
                for dev, data in self.water_heater.items():
                    if data is not None:
                        if len(data) > 45:
                            response["water_heater"] = True
            else:
                response["water_heater"] = False

            return response
        except Exception as e:
            logging.exception(e)
            return {}

    def key_in_json(self, key):
        """
        :param key: Checks if the key exists inside the self.d json
        :return: boolean True if exists
        """
        try:
            return True if key in self.d else False
        except Exception as e:
            print("Exception in Recommend.key_in_json")
            logging.exception(e)

    def search_and_recommend(self):
        """
        Calls all the required functions to calculate
         new recommendations for each user case.

        :return: (String [] self.recs) contains new recommendations if any are found.

        example return:
        [ "Water Heater on for over and hour",
        "Washing Machine saves energy if activated at night"]
        """
        try:
            # self.heater_averaging()
            if self.validity_json["water_heater"]:
                self.check_water_heater(self.recs)
            if self.hum is not None and self.out_hum is not None and self.hum_thresh is not None:
                self.recs = self.check_humidity(self.recs)
            if self.occ_60:
                self.recs = self.check_occupancy(self.recs)
            if self.night_power_discount == 1:
                self.recs = self.check_washing_machine(self.recs)
            if self.validity_json["lights"]:
                self.check_and_predict_lights(self.recs)
            if self.validity_json["thermostat"]:
                self.check_and_predict_thermostat(self.recs)
            if self.validity_json["hvac"]:
                self.check_and_predict_ac(self.recs)

            if self.co2_thresh is not None and self.co2 is not None:
                self.recs = self.check_co2(self.recs)
            self.recs = self.generic_heating(self.recs)
            if self.recs:
                self.recs = self.config_ops.handle_new_recommendations(self.recs)
            self.recs = self.weekly_recs(self.recs)
            return self.recs
        except Exception as e:
            print("Exception in Recommend.search_and_recommend check_predictions")
            logging.exception(e)

    def generic_heating(self, new_recs):
        if self.generic_upper_hvac:
            new_recs.append({
                "message": self.r13,
                "rate": self.r13_rate,
                "number": self.no13,
                "device": "hvac"
            })
        if self.generic_lower_hvac:
            new_recs.append({
                "message": self.r14,
                "rate": self.r14_rate,
                "number": self.no14,
                "device": "hvac"
            })
        if self.generic_upper_thermostat:
            new_recs.append({
                "message": self.r15,
                "rate": self.r15_rate,
                "number": self.no15,
                "device": "thermostat"
            })
        if self.generic_lower_thermostat:
            new_recs.append({
                "message": self.r16,
                "rate": self.r16_rate,
                "number": self.no16,
                "device": "thermostat"
            })
        return new_recs

    def weekly_recs(self, new_recs):
        """
        Checks all the weekly recommendation modules and returns the recommendations,
        if any are produced
        :return: recommendation
        """
        # GENERAL 1 - 101
        if self.key_in_json('weekly_consumption'):
            weekly_consumption = self.weekly_consumption_check(self.d['weekly_consumption'])
            if weekly_consumption:
                new_recs.append(weekly_consumption)

        # GENERAL 2 - 102
        if self.key_in_json('aggregate_savings'):
            weekly_savings = self.weekly_savings_aggregate(self.d['aggregate_savings'])
            if weekly_savings:
                new_recs.append(weekly_savings)

        # GENERAL 3 - 103
        if self.generic_change_setpoint:
            new_recs.append({
                "message": self.r103,
                "rate": self.r103_rate,
                "number": self.no103
            })
            self.config_ops.set_field("g_sent3", "1")

        # GENERAL 4 - 104
        if self.generic_turn_off_standby:
            new_recs.append({
                "message": self.r104,
                "rate": self.r104_rate,
                "number": self.no104
            })
            self.config_ops.set_field("g_sent4", "1")

        # GENERAL 5 - 105
        if self.generic_open_windows:
            new_recs.append({
                "message": self.r105,
                "rate": self.r105_rate,
                "number": self.no105
            })
            self.config_ops.set_field("g_sent5", "1")

        # GENERAL 6 - 106
        if self.key_in_json('weekly_smartplugs'):
            plugs = self.smartplugs(self.d['weekly_smartplugs'])
            if plugs:
                new_recs.append(plugs)

        # GENERAL 7 - 107
        if self.generic_efficient_heating:
            new_recs.append({
                "message": self.r107,
                "rate": self.r107_rate,
                "number": self.no107
            })
            self.config_ops.set_field("g_sent5", "1")
        return new_recs

    def smartplugs(self, args):
        """
        Checks the client's smartplugs for unusual weekly consumption
        :return: recommendation
        """
        try:
            msg = ""
            for plug in args.keys():
                this_week_data = args[plug]["current_week"]
                last_week_data = args[plug]["previous_week"]
                # interval = (str_to_dt(this_week_data[1][0]) - str_to_dt(this_week_data[0][0])).seconds//60
                tw_kwh = this_week_data
                lw_kwh = last_week_data
                # Missing Data percentage calculation
                # if this_week_data is not None and last_week_data is not None:
                #     twl = len(this_week_data)
                #     pwl = len(last_week_data)
                #     if abs(twl - pwl) < 0.2 * twl:
                #         if twl >= pwl:
                #             lw_miss_perc = round((twl - pwl) * 100 / twl, 3)
                #             tw_miss_perc = None
                #         else:
                #             tw_miss_perc = round((pwl - twl) * 100 / pwl, 3)
                #             lw_miss_perc = None
                #
                #         # kWh calculation -> missing data adjust
                #         tw_kwh = 0
                #         for i in this_week_data:
                #             tw_kwh += i[-1] / interval
                #         if tw_miss_perc:
                #             tw_kwh += tw_miss_perc / 100 * tw_kwh
                #         tw_kwh = round(tw_kwh, 2)
                #
                #         lw_kwh = 0
                #         for j in last_week_data:
                #             lw_kwh += j[-1] / interval
                #         if lw_miss_perc:
                #             lw_kwh += lw_miss_perc / 100 * lw_kwh
                #         lw_kwh = round(lw_kwh, 2)

                if tw_kwh < 0 or lw_kwh < 0:
                    pass
                else:
                    # if tw_kwh > lw_kwh * 1.5 and lw_kwh > 100:
                    if tw_kwh > lw_kwh * 1.5:
                        # prc = round((tw_kwh - lw_kwh) / 1000, 2)
                        prc = round((tw_kwh - lw_kwh), 3)
                        if self.language == 'GR':
                            if msg == "":
                                msg = "Αυτή την εβδομάδα οι παρακάτω πρίζες είχαν ασυνήθιστα υψηλή κατανάλωση σε σχέση με την προηγούμενη εβδομάδα: "
                                msg += plug + ": " + str(prc) + " kWh παραπάνω"
                            else:
                                msg += ", " + plug + ": " + str(prc) + " kWh παραπάνω"
                        else:
                            if msg == "":
                                msg = "This week the following plugs had unusually high consumption compared to " \
                                      "last week: "
                                msg += plug + " up by " + str(prc) + " kWh"
                            else:
                                msg += ", " + plug + " up by " + str(prc) + " kWh"
            if msg:
                self.config_ops.set_field("g_sent6", "1")
                return {
                    "message": msg,
                    "rate": self.r106_rate,
                    "number": self.no106
                }
            else:
                return None
        except Exception as e:
            print("Exception in Recommend.weekly_consumption_check")
            logging.exception(e)
            return None

    def weekly_consumption_check(self, args):
        """
        Calculates the client's weekly consumption and compares it to last week's
        :return: recommendation
        """
        try:
            msg = ""

            this_week_data = args["current_week"]
            last_week_data = args["previous_week"]
            tw_kwh = this_week_data
            lw_kwh = last_week_data
            # Missing Data percentage calculation
            # twl = len(this_week_data)
            # pwl = len(last_week_data)
            # interval = (str_to_dt(this_week_data[1][0]) - str_to_dt(this_week_data[0][0])).seconds // 60
            # if abs(twl - pwl) < 0.2 * twl:
            #     if twl >= pwl:
            #         lw_miss_perc = round((twl - pwl) * 100 / twl, 3)
            #         tw_miss_perc = None
            #     else:
            #         tw_miss_perc = round((pwl - twl) * 100 / pwl, 3)
            #         lw_miss_perc = None
            #
            #     # kWh calculation -> missing data adjust
            #     tw_kwh = 0
            #     for i in this_week_data:
            #         tw_kwh += i[-1] / interval
            #     if tw_miss_perc:
            #         tw_kwh += tw_miss_perc / 100 * tw_kwh
            #     tw_kwh = round(tw_kwh, 2)
            #
            #     lw_kwh = 0
            #     for j in last_week_data:
            #         lw_kwh += j[-1] / interval
            #     if lw_miss_perc:
            #         lw_kwh += lw_miss_perc / 100 * lw_kwh
            #     lw_kwh = round(lw_kwh, 2)

            if tw_kwh < 0 or lw_kwh < 0:
                pass
            else:
                if tw_kwh > lw_kwh:
                    if self.language == 'GR':
                        sub_str = "περισσότερο"
                    else:
                        sub_str = "more"
                else:
                    if self.language == 'GR':
                        sub_str = "λιγότερο"
                    else:
                        sub_str = "less"

                prc = round(abs(tw_kwh - lw_kwh) * 100 / lw_kwh, 1)
                if self.language == 'GR':
                    # msg = "Αυτή την εβδομάδα η κατανάλωσή σου ήταν " + str(round((tw_kwh / 1000), 2)) + " kWh, " + str(
                    msg = "Αυτή την εβδομάδα η κατανάλωσή σου ήταν " + str(round(tw_kwh, 3)) + " kWh, " + str(
                        prc) + "% " + str(
                        sub_str) + " από την προηγούμενη εβδομάδα."
                else:
                    # msg = "This week your consumption was " + str(round((tw_kwh / 1000), 2)) + " kWh, " + str(
                    msg = "This week your consumption was " + str(round(tw_kwh, 3)) + " kWh, " + str(
                        prc) + "% " + str(
                        sub_str) + " compared to last week."

            # else:
            #     pass
            if msg:
                self.config_ops.set_field("g_sent1", "1")
                return {
                    "message": msg,
                    "rate": self.r101_rate,
                    "number": self.no101
                }
            else:
                return None
        except Exception as e:
            print("Exception in Recommend.weekly_consumption_check")
            logging.exception(e)
            return None

    def weekly_savings_aggregate(self, args):
        """
        Calculates the client's weekly savings aggregate
        :return: recommendation
        """
        msg = ""
        actual = 0
        potential = 0
        if args:
            for val in args:
                if val[1] == 1:
                    actual += float(val[0])
                elif val[1] == 0:
                    potential += float(val[0])

            actual = round((actual / 1000), 2)
            potential = round((potential / 1000), 2)

            if actual > 0:
                if self.language == 'GR':
                    msg = 'Αυτή την εβδομάδα οι δράσεις εξοικονόμησης οδήγησαν σε πραγματική εξοικονόμηση ' + str(actual) + ' kWh.'
                    if potential > 0:
                        msg += 'Αν υλοποιούνταν όλες οι δράσεις, θα εξοικονομούνταν επιπλέον ' + str(potential) + ' kWh.'
                else:
                    msg = "This week's recommendations resulted in actual savings of " + str(actual) + " kWh."
                    if potential > 0:
                        msg += " If all the recommended actions were followed, they could result in an " \
                               "extra " + str(potential) + " kWh of savings."

            else:
                if potential > 0:
                    if self.language == 'GR':
                        msg = "Αυτή την εβδομάδα οι δράσεις εξοικονόμησης θα οδηγούσαν σε εξοικονόμηση " + str(potential) \
                              + " kWh, αν υλοποιούνταν όλες οι δράσεις."
                    else:
                        msg = "This week's recommendations could result in " + str(potential) \
                              + " kWh of savings, if the recommended actions were followed."
        if msg:
            self.config_ops.set_field("g_sent2", "1")
            return {
                "message": msg,
                "rate": self.r102_rate,
                "number": self.no102
            }
        else:
            return None


    # def heater_averaging(self):
    # """
    # Changes the config fields corresponding to the client's last 3 uses of the water heater
    # """
    # try:
    #     for name, value in self.devices.items():
    #         if name == "water heater":
    #             if value > 100:
    #                 if not self.config_ops.heater["heater_is_on"]:
    #                     self.config_ops.set_field("heater_is_on", "1", section="heater_averaging")
    #                     self.config_ops.set_field("heater_on", dt_to_str(self.date), section="heater_averaging")
    #             else:
    #                 if self.config_ops.heater["heater_is_on"]:
    #                     self.config_ops.set_field("heater_is_on", "0", section="heater_averaging")
    #                     dur = self.date - self.config_ops.heater["heater_on"]
    #                     if dur > delta(minutes=10):
    #                         self.config_ops.set_field("duration_1", self.config_ops.heater["duration_2"],
    #                                                   section="heater_averaging")
    #                         self.config_ops.set_field("duration_2", self.config_ops.heater["duration_3"],
    #                                                   section="heater_averaging")
    #                         self.config_ops.set_field("duration_3", str(int(dur.seconds / 60)),
    #                                                   section="heater_averaging")
    # except Exception as e:
    #     logging.exception(e)
    #     print("Exception in Recommend.heater_averaging")
    #     pass
    # return None

    # def check_water_heater(self, new_recs):
    #     """Recommends to power off the water heater
    #     if it's left ON for more than an hour.
    #
    #
    #     :param string [] new_recs: Recommendation matrix, append any new recommendation and return
    #
    #     :return: (String [] new_recs) contains new recommendations if any are found.
    #     """
    #     try:
    #         # Heater Token
    #         devs_json = self.read_data.read_client_info(self.client)
    #         plugs = devs_json['plugs']
    #         if plugs:
    #             for p in plugs:
    #                 device_id = p["device_id"]
    #                 map_name = p["map"]
    #                 type_ = p["type_"]
    #                 if map_name == "water heater":
    #                     duration = self.config_ops.get_heater_average()
    #                     heat = self.heater_duration_average_check(device_id, type_, duration)
    #                     if heat:
    #                         if self.r1 not in new_recs:
    #                             new_recs.append({
    #                                 "message": self.r1 + str(duration) + " minutes",
    #                                 "rate": self.r1_rate,
    #                                 "number": self.no1
    #                             })
    #     except Exception as e:
    #         print("Exception in Recommend.check_occupancy DEVICES")
    #         logging.exception(e)
    #     return new_recs

    # def heater_duration_average_check(self, dev_id, type_, duration):
    #     """
    #     Calculates the duration of the last use of the client's water heater
    #     :return: 1 if successful
    #     """
    #     fromtime = self.date - delta(minutes=duration)
    #     heater_data = self.api.get_measurement_local(user=self.client,
    #                                                  device_id=dev_id,
    #                                                  totime=self.date,
    #                                                  type_=type_,
    #                                                  fromtime=fromtime)
    #     if heater_data:
    #         if heater_data["values"]:
    #             heaterlist = []
    #             entries = heater_data["values"]
    #             for u in entries:
    #                 heaterlist.append(1 if u[-1] > 100 else 0)
    #             if heaterlist.count(1) > 0.9 * duration and (heaterlist[-1] == 1):
    #                 return 1
    #             else:
    #                 return 0
    #         # TODO Are the 2 return None right?
    #         return None
    #     return None

    def check_humidity(self, new_recs):
        """Recommends to air the house
        if inner humidity - outer humidity > hum_thresh.
        :param string [] new_recs: Recommendation matrix, append any new recommendation and return
        :return: (String [] new_recs) contains new recommendations if any are found.
        """
        try:
            if self.hum - self.out_hum > self.hum_thresh:
                # if self.r2 not in new_recs:
                new_recs.append({
                    "message": self.r2,
                    "rate": self.r2_rate,
                    "number": self.no2
                })
        except Exception as e:
            logging.exception(e)
            print("Exception in Recommend.check_occupancy DEVICES")
        return new_recs

    def check_co2(self, new_recs):
        """Recommends airing the house if co2 > co2 threshold.
        :param string [] new_recs: Recommendation matrix, append any new recommendation and return
        :return: (String [] new_recs) contains new recommendations if any are found.
        """
        try:
            print(self.co2,self.co2_thresh)
            if self.co2 > self.co2_thresh:
                # if self.r3 not in new_recs:
                new_recs.append({
                    "message": self.r3,
                    "rate": self.r3_rate,
                    "number": self.no3
                })
        except Exception as e:
            logging.exception(e)
            print("Exception in Recommend.check_occupancy DEVICES")
        return new_recs

    def check_occupancy(self, new_recs):
        """Recommends to power off any device that is
        left ON, if the house is unoccupied for more than an hour.

        :param string [] new_recs: Recommendation matrix, append any new recommendation and return.

        :return: (String [] new_recs) contains new recommendations if any are found.

        example return:
        ["Turn off the TV",
        "Turn off the Oven"]
        """
        # DEVICES
        try:
            for name, status in self.devices.items():
                if (not name == "fridge") and (not name == "Fridge"):
                    if status > 10:
                        r = self.r6 + " " + str(name)
                        # if r not in new_recs:
                        # "DEVICE RECOMMENDATION"
                        new_recs.append({
                            "message": r,
                            "rate": self.r6_rate,
                            "number": self.no6,
                            "device": name
                        })
        except Exception as e:
            logging.exception(e)
            print("Exception in Recommend.check_occupancy DEVICES")
            pass
        return new_recs

    def check_washing_machine(self, new_recs):
        """Recommends to function the washing machine
        at power discount times , if the user has night
        power discount available.

        :param string [] new_recs: Recommendation matrix, append any new recommendation and return
        :param string [] data: Object Initialization Input Matrix

        :return: (String [] new_recs) contains new recommendations if any are found.
        """
        try:
            for key in self.devices.keys():
                if key == 'washing_machine':
                    if float(self.devices[key]) > 20:
                        # if self.r7 not in new_recs:
                        new_recs.append({
                            "message": self.r7,
                            "rate": self.r7_rate,
                            "number": self.no7
                        })
                    return new_recs
        except Exception as e:
            print("Exception in Recommend.check_washing_machine")
            logging.exception(e)
            return new_recs

    def check_water_heater(self, new_recs):
        """
        """
        try:
            zero_counter = 0
            first = True
            for key, data in self.water_heater.items():
                if data is not None:
                    # Check if open
                    on_counter = 0
                    datalength = len(data)
                    for tms in reversed(data):
                        if first:
                            if tms[1] < 10:
                                print(first)
                                break
                            else:
                                first = False
                        if tms[1] >= 10:
                            on_counter += 1
                        else:
                            zero_counter += 1
                            print(zero_counter)
                            if zero_counter >= 0.1 * datalength:
                                break
                    if on_counter > self.water_heater_threshold:
                        msg = self.r1 + str(self.water_heater_threshold) + " minutes."
                        new_recs.append({
                            "message": msg,
                            "rate": self.r1_rate,
                            "number": self.no1,
                            "device": key
                        })
            return new_recs
        except Exception as e:
            print("Exception in Recommend.check_water_heater")
            logging.exception(e)
            return new_recs

    def check_and_predict_ac(self, new_recs):
        """Calls the prediction module to return the predicted
        light_status, Hvac On/Off, Hvac SetTemp and Light Dimmer Level data.
        Compare this data to live sensor data from the
        smart home API and output recommendations based
        on their deviation.

        :param string [] new_recs: Recommendation matrix, append any new recommendation and return

        :return: (String [] new_recs) contains new recommendations if any are found.

        Loads the decision tree and random forest
        models and returns the predicted models' output.
        Output: Dimmer of the lights
                HVAC setTemp
                HVAC ON/OFF

        :return: (int best_dimmer, int best_set_temp, int best_on_off) .

        example return:
        90, 25, 1
        """
        try:
            if self.thermal_model_AC and \
                    self.tem is not None and \
                    self.hum is not None and \
                    self.out_tmp is not None and \
                    self.out_hum is not None and \
                    self.comfort["hvac"]["thermal_comfort"] is not None and \
                    self.hvac_settemp is not None and \
                    self.hvac_status is not None and \
                    self.date:
                features = {
                    "temperature": self.tem,
                    "humidity": self.hum,
                    "temperature_out": self.out_tmp,
                    "humidity_out": self.out_hum,
                    "thermal_comfort": self.comfort["hvac"]["thermal_comfort"],
                    "date": self.date
                }
                thermal_comfort_ac = ThermalComfortHvac(args=features, sav=self.thermal_model_AC, train=self.train)
                heat, cool, mode = thermal_comfort_ac.predict(features)
                # print(f"Thermostat: Heat: {heat}, cool: {cool}, mode: {mode}, self.settemp: {self.hvac_settemp}, self.status: {self.hvac_status}")
                if mode == 0:
                    if 1 <= self.hvac_status <= 3:
                        # if self.r4 not in new_recs:
                        new_recs.append({
                            "message": self.r4,
                            "rate": self.r4_rate,
                            "number": self.no4,
                            "device": "hvac"
                        })
                    else:
                        pass
                else:
                    if self.hvac_status == 1 or self.hvac_status == 2:
                        # COOL
                        if cool - self.hvac_settemp > 0.99:
                            cool = round(cool)
                            val3 = self.r10 + " " + str(cool) + ' C'
                            # if val3 not in new_recs:
                            new_recs.append({
                                "message": val3,
                                "rate": self.r10_rate,
                                "number": self.no10,
                                "device": "hvac",
                                "setTemp": cool
                            })
                    elif self.hvac_status == 1 or self.hvac_status == 3:
                        # HEAT
                        if self.hvac_settemp - heat > 0.99:
                            heat = round(heat)
                            val2 = self.r9 + " " + str(heat) + ' C'
                            # if val2 not in new_recs:
                            new_recs.append({
                                "message": val2,
                                "rate": self.r9_rate,
                                "number": self.no9,
                                "device": "hvac",
                                "setTemp": heat
                            })
                return new_recs
        except Exception as e:
            print("Exception in Recommend.check_and_predict_ac")
            logging.exception(e)
            return new_recs

    def check_and_predict_thermostat(self, new_recs):
        try:
            if self.thermal_model_thermostat and \
                    self.tem is not None and \
                    self.hum is not None and \
                    self.out_tmp is not None and \
                    self.out_hum is not None and \
                    self.comfort["thermostat"]["thermal_comfort"] is not None and \
                    self.thermostat_settemp is not None and \
                    self.thermostat_status is not None and \
                    self.date:
                features = {
                    "temperature": self.tem,
                    "humidity": self.hum,
                    "temperature_out": self.out_tmp,
                    "humidity_out": self.out_hum,
                    "thermal_comfort": self.comfort["thermostat"]["thermal_comfort"],
                    "date": self.date
                }
                tst = ThermalComfortThermostat(args=features, sav=self.thermal_model_thermostat, train=self.train)
                setpoint, mode = tst.predict(features)
                # print(f"Thermostat: Setpoint: {setpoint}, mode: {mode}, self._settemp: {self.thermostat_settemp}, self.status: {self.thermostat_status}")
                if mode == 0:
                    if self.thermostat_status == 1:
                        # if self.r4 not in new_recs:
                        r = self.r6 + " thermostat"
                        new_recs.append({
                            "message": r,
                            "rate": self.r4_rate,
                            "number": self.no6,
                            "device": "thermostat"
                        })
                    else:
                        pass
                else:
                    if self.thermostat_status == 1:
                        if setpoint - self.thermostat_settemp > 0.99:
                            setpoint = round(setpoint * 2) / 2
                            val3 = self.r12 + " " + str(setpoint) + ' C'
                            # if val3 not in new_recs:
                            new_recs.append({
                                "message": val3,
                                "rate": self.r12_rate,
                                "number": self.no12,
                                "device": "thermostat",
                                "setTemp": setpoint
                            })
                        elif self.thermostat_settemp - setpoint > 0.99:
                            setpoint = round(setpoint*2) / 2
                            val2 = self.r11 + " " + str(setpoint) + ' C'
                            # if val2 not in new_recs:
                            new_recs.append({
                                "message": val2,
                                "rate": self.r11_rate,
                                "number": self.no11,
                                "device": "thermostat",
                                "setTemp": setpoint
                            })
                return new_recs
        except Exception as e:
            print("Exception in Recommend.check_and_predict_ac")
            logging.exception(e)
            return new_recs

    def check_and_predict_lights(self, new_recs):
        try:
            for key in self.lights:
                if self.visual_model and \
                        self.lights[key]["luminance"] is not None and \
                        self.ghi is not None and \
                        self.lights[key]["visual_comfort"] is not None and \
                        self.lights[key]["dimmer"] is not None and \
                        self.lights[key]["status"] is not None and \
                        self.date:
                    features = {
                        "luminance": self.lights[key]["luminance"],
                        "ghi": self.ghi,
                        "visual_comfort": self.lights[key]["visual_comfort"],
                        "date": self.date
                    }
                    vcl = VisualComfortLights(args=None, sav=self.visual_model, train=self.train)
                    dimmer, mode = vcl.predict(features)
                    if dimmer > 100:
                        dimmer = 100
                    elif dimmer < 0:
                        dimmer = 0
                    dimmer = round(dimmer, -1)
                    if self.lights[key]["status"] == 1:
                        if self.lights[key]["dimmer"] - dimmer > 9.9:
                            val1 = self.r8 + " " + str(dimmer) + f' % for device {key}'
                            # if val1 not in new_recs:
                            new_recs.append({
                                "message": val1,
                                "rate": self.r8_rate,
                                "number": self.no8,
                                "device": "lights",
                                "dimmer": dimmer
                            })
            return new_recs
        except Exception as e:
            print("Exception in Recommend.check_and_predict_lights")
            logging.exception(e)
            return new_recs


def dt_to_str(dat):
    try:
        return dat.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
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
        logging.exception(e)
