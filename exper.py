
from apscheduler.schedulers.background import BackgroundScheduler
import datetime 

# Create a scheduler
scheduler = BackgroundScheduler()
# Add the job to the scheduler - runs the 'job' function every minute
scheduler.add_job(collectData, 'interval', minutes=0.5)
# Start the scheduler
scheduler.start()

# using now() to get current time 
current_time = datetime.datetime.now()
print(current_time) 
print(type(current_time))