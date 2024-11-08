import pandas as pd
import datetime
from plyer import notification
import json
import schedule
import time

filepath = "./data/test.xlsx"
df = pd.read_excel(filepath)
# Convert the 'Registration_Date' to datetime if necessary
df['Registration_Date'] = pd.to_datetime(df['Registration_Date'], format='%Y-%m-%d').dt.date

def load_config(config_path='config.json'):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

# Load user preferences
config = load_config()

def send_reminders():
    reminder_date = today + datetime.timedelta(days=reminder_days_before)
    
    # Filter the upcoming events to include only those with the reminder date
    events_to_remind = upcoming_events[upcoming_events['Registration_Date'] == reminder_date]
    
    for _, event in events_to_remind.iterrows():
        sender = event['Sender']
        event_name = event['Event']
        date = event['Registration_Date']
        link = event['Link']
    
        notification.notify(
            title=f"Reminder: {event_name}",
            message=f"Deadline: {date} (in {reminder_days_before} days)\nLink: {link}",
            timeout=60  # Notification duration in seconds
        )

# Get today's date
today = datetime.datetime.today().date()

# Get the user-defined reminder lead time from the config
reminder_days_before = config["reminder_lead_time"]
reminder_date = today + datetime.timedelta(days=reminder_days_before)

# Filter the rows where the registration date is today or in the future
upcoming_events = df.loc[df['Registration_Date'] >= today]

'''
notification.notify(
    title="Test Notification",
    message="This is a test reminder!",
    timeout=10  # Notification duration in seconds
)
'''

 
# Extract the time from the config (e.g., "08:00")
reminder_time_str = config["reminder_time"]
reminder_time = datetime.datetime.strptime(reminder_time_str, "%H:%M").time()

# Set the time for the reminder
reminder_datetime = datetime.datetime.combine(today, reminder_time)

# Check if the reminder date matches today
if datetime.datetime.now() >= reminder_datetime:
    # Trigger the reminder notifications
    send_reminders()
    
    
# Adjust the reminder frequency based on user preferences
if config["notification_frequency"] == "daily":
    schedule.every().day.at(reminder_time_str).do(send_reminders)
elif config["notification_frequency"] == "weekly":
    schedule.every().week.at(reminder_time_str).do(send_reminders)
    

def update_config(new_settings):
    config.update(new_settings)
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)


# Example: Change reminder time
# update_config({"reminder_time": "11:00"})


# while True:
#     schedule.run_pending()  # Check if any reminder is due
#     time.sleep(60)  # Check every minute

    



    
