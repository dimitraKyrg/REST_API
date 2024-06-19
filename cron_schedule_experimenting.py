from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import time

# Shared data structure
results = {}

def my_scheduled_function(param, result_store, key):
    result = f"Processed {param}"
    result_store[key] = result

def main():
    global results
    my_variable = "Task Input"

    # Create the scheduler
    scheduler = BackgroundScheduler()

    # Add job to scheduler
    scheduler.add_job(
        my_scheduled_function,
        IntervalTrigger(seconds=10),  # For demonstration, runs every 10 seconds
        args=[my_variable, results, 'task1']
    )

    # Start the scheduler
    scheduler.start()

    print("Scheduler started. Job will run every 10 seconds.")

    try:
        while True:
            time.sleep(1)
            if 'task1' in results:
                print(f"Result from scheduled task: {results['task1']}")
                # Optionally reset or clear the result
                #results['task1'] = None
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("Scheduler shut down.")

if __name__ == "__main__":
    main()
