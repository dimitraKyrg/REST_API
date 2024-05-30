(defrule BR_Service
    (service BR)
    =>
    (printout t crlf "Would you like to book or return a car? ("B" for book / "R" for return)" crlf)
    (assert (br (upcase(read))))
)

(defrule Book_Service
    (br B)
    =>
    (printout t crlf "Are you a first-time user? (Y/N)" crlf)
    (assert (b (upcase(read))))
)

(defrule Premium_Member
    (b N)
    =>
    (printout t crlf "Are you a Premium status member? (Y/N)" crlf)
    (assert (p (upcase(read))))
)

(deftemplate person(slot name)(slot age)(multislot hobbies))

(defrule check-temperature
    (temp ?temp)
    (test (> ?temp 30))
    =>
    (printout t "The temperature is above 30 degrees." crlf)
)