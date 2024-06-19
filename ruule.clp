(defrule compareHvacTemperatures
    (hvac_temperature_after ?hvac_temperature_after)
    (hvac_temperature_before ?hvac_temperature_before)
    =>
    (if (> ?hvac_temperature_after ?hvac_temperature_before)
 	then
		(assert (Hvac temperature got higher))
 	else
		(assert (Hvac temperature got lower))    
))

(defrule compareSensorTemperatures
    (sensor_temperature_after ?sensor_temperature_after)
    (sensor_temperature_before ?sensor_temperature_before)
    =>
    (if (> ?sensor_temperature_after ?sensor_temperature_before)
 	then
		(assert (Sensor temperature got higher))
 	else
		(assert (Sensor temperature got lower))    
))

(defrule compareHvacHumidities
    (hvac_humidity_after ?hvac_humidity_after)
    (hvac_humidity_before ?hvac_humidity_before)
    =>
    (if (> ?hvac_humidity_after ?hvac_humidity_before)
 	then
		(assert (Hvac humidity got higher))
 	else
		(assert (Hvac humidity got lower))
))

(defrule compareSensorHumidities
    (sensor_humidity_after ?sensor_humidity_after)
    (sensor_humidity_before ?sensor_humidity_before)
    =>
    (if (> ?sensor_humidity_after ?sensor_humidity_before)
 	then
		(assert (Sensor humidity got higher))
 	else
		(assert (Sensor humidity got lower))
))

(defrule compareHvacLuminance
    (hvac_luminance_after ?hvac_luminance_after)
    (hvac_luminance_before ?hvac_luminance_before)
    =>
    (if (> ?hvac_luminance_after ?hvac_luminance_before)
 	then
		(assert (Hvac luminance got higher))
 	else
		(assert (Hvac luminance got lower))
))

(defrule compareSensorLuminance
    (sensor_luminance_after ?sensor_luminance_after)
    (sensor_luminance_before ?sensor_luminance_before)
    =>
    (if (> ?sensor_luminance_after ?sensor_luminance_before)
 	then
		(assert (Sensor luminance got higher))
 	else
		(assert (Sensor luminance got lower))
))

(defrule compare-co2
    (co2_after ?co2_after)
    (co2_before ?co2_before)
    =>
    (if (> ?co2_after ?co2_before)
 	then
		(assert (co2 got higher))
 	else
		(assert (co2 got lower))
     )
)

; check water heater rules

(defrule check_water_heater1
    (water_heater_before on)(water_heater_after off)
    =>
    (assert (water heater went off))
)

(defrule check_water_heater2
    (water_heater_before off)(water_heater_after on)
    =>
    (assert (water heater went on))
)
(defrule check_water_heater3
    (water_heater_before on)(water_heater_after on)
    =>
    (assert (water heater stayed on))
)

(defrule check_water_heater4
    (water_heater_before off)(water_heater_after off)
    =>
    (assert (water heater stayed off))
)

; check HVAC rules

(defrule check_HVAC1
    (HVACr_before on)(HVAC_after off)
    =>
    (assert (HVAC went off))
)

(defrule check_HVAC2
    (HVAC_before off)(HVAC_after on)
    =>
    (assert (HVAC went on))
)
(defrule check_HVAC3
    (HVAC_before on)(HVAC_after on)
    =>
    (assert (HVAC stayed on))
)

(defrule check_HVAC4
    (HVAC_before off)(HVAC_after off)
    =>
    (assert (HVAC stayed off))
)

(defrule checkRule1_true
    (water heater went off)(Number1 was recommended)
    =>
    (assert (Number1 was followed))
)

(defrule checkRule1_false
    (water heater stayed on)(Number1 was recommended)
    =>
    (assert (Number1 was dissmised))
)

(defrule checkRule2_true
    (Humididty got lower)(Number2 was recommended)
    =>
    (assert (Number1 was followed))
)

(defrule checkRule2_false
    (not(Humididty got lower))(Number2 was recommended)
    =>
    (assert (Number2 was dissmised))
)

(defrule checkRule3_true
    (co2 got lower)(Number3 was recommended)
    =>
    (assert (Number3 was follwed))
)

(defrule checkRule3_false
    (not(co2 got lower))(Number3 was recommended)
    =>
    (assert (Number3 was dissmised))
)

(defrule checkRule4_true
    (HVAC went off)(Number4 was recommended)
    =>
    (assert (Number4 was followed))
)

(defrule checkRule4_false
    (HVAC stayed on)(Number4 was recommended)
    =>
    (assert (Number4 was dissmised))
)

(defrule checkRule8_true
    (lighting got lower)(Number8 was recommended)
    =>
    (assert (Number8 was follwed))
)

(defrule checkRule8_false
    (not(lighting got lower))(Number8 was recommended)
    =>
    (assert (Number8 was dissmised))
)

;example of rule that uses numerical comparison

;(defrule check-temperature
;    (temp_before ?temp_before)
;    (test (> ?temp_before 30))
;    =>
;    (printout t "The temperature is above 30 degrees." crlf)
;)