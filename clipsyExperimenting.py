import clips


def lala():
    print('25')

RULES = [
    """
    (defrule book-service
      =>
      (bind ?answer (polar-question "Are you a first-time user?"))
      (assert (first-time-user ?answer)))
    """,
    """
    (defrule first-timer
      (first-time-user "Yes")
      =>
      (bind ?answer (polar-question "Do you like reading books?"))
      (assert (likes-reading-books ?answer)))
    """
]

k = 0
env = clips.Environment()
env.clear()
rule_file = 'ruule.CLP'
env.call('create$', clips.Symbol('service'), 'BR')
env.load(rule_file)
print("What kind of service needed? ('BR' for book/return car / 'EM' for emergency)")
input = input()
env.assert_string("(water_heater_before on)")
#env.assert_string("(water_heater_after off)")
env.assert_string("(service BR)")
env.assert_string("(the pump is on)")
env.assert_string("(temp_after 70)")
env.assert_string("(Recommendation1 recommended)")
env.assert_string("(temp_before 60)")
env.assert_string("(hum_before 60)")
env.assert_string("(hum_after 30)")
env.assert_string("(lighting_before 60)")
env.assert_string("(lighting_after 30)")
#env.eval("(deftemplate person(slot name)(slot age)(multislot hobbies))")
#env.assert_string('(person (name "Jack Smith") (age 23) (hobbies movies golf))')
env.run()
#a = env.eval("service == BR")
#print(a)

for fact in env.facts():
  print('-------------------------')

  print(fact)
  print(type(fact))

print(type(env._facts.facts()))
print(env._facts.facts())
print(list(env._facts.facts()))
print(type(str(list(env._facts.facts())[0])))
print((list(env._facts.facts())[0]))

lala = []
for i in range(len(list(env._facts.facts()))):
   lala.append(str(list(env._facts.facts())[i])[1:-1])
   print(list(env._facts.facts())[i])

print(lala)
