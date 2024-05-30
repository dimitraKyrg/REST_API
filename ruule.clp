(defrule compare-temperatures
    (temp ?temp)
    (temp_before ?temp_before)
    (test (> ?temp ?temp_before))
    =>
    (printout t "The temperature got higher." crlf)
)


(defrule check-temperature
    (temp ?temp)
    (test (> ?temp 30))
    =>
    (printout t "The temperature is above 30 degrees." crlf)
)



