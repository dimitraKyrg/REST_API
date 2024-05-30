from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
import time

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

app = Flask(__name__)

# Define a function to be executed by the scheduler
def job():
    print("Scheduler is running...")
    post(EVENTRULESET, {'color': 'red' })

# Define a route for the Flask app
@app.route('/')
def index():
    return 'Flask App is running...'

# Create a scheduler
scheduler = BackgroundScheduler()
# Add the job to the scheduler - runs the 'job' function every minute
scheduler.add_job(job, 'interval', minutes=0.5)
# Start the scheduler
scheduler.start()
while True:
    time.sleep(1)
    #scheduler.shutdown(wait=False)

'''
if __name__ == '__main__':

    # Run the Flask app
    #app.run(debug=True)
'''