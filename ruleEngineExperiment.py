'''
from durable.lang import *


with ruleset('test'):
    print(m)
    print(m.__dict__)
    print(dir(m))

    print(c)
    
    @when_all(m.subject == 'World')
    
    def say_hello(c):
        print ('Hello {1}'.format(c.m.a))

post('test', { 'subject': 'World' , 'subject2' :'hello'})
'''

from durable.lang import post
from simple_speech import Speech
from durable.lang import *
from durable.lang import ruleset, when_all, assert_fact, c, m
from durable_rules_tools.rules_utils import new_ruleset, Set, Subject

speaker = Speech()

EVENTRULESET = new_ruleset()
with ruleset(EVENTRULESET):
    # this rule will trigger as soon as three events match the condition
    @when_all(m.color=='red')
    def see_red(c):
        speaker.say(f'I see red')
        c.assert_fact({'status': 'danger'})
        
    @when_all(m.color!='red')
    def not_red(c):
        speaker.say(f'I see {c.m.color}')
        c.assert_fact({'status': 'safe'})

    @when_all( m.status == 'danger')
    def dangerous(c):
        speaker.say(f'That is dangerous.')
        c.retract_fact({'status': 'danger'})
        
    @when_all( m.status == 'safe')
    def safe(c):
        speaker.say(f'That is safe.')
        c.retract_fact({'status': 'safe'})

post(EVENTRULESET, {'color': 'red' })
post(EVENTRULESET, {'color': 'green'})