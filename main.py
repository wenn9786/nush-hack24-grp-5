import pandas as pd
import requests
import json
import datetime
import schedule
import time
from io import BytesIO
from plyer import notification

# Google Apps Script URL to trigger the Excel file export
web_app_url = 'https://script.google.com/macros/s/AKfycbwinajixME2cZiQvyCJANDLng-dCte4g4ERzY2S6C79qPCbt3Uojuvk6FnYrE8u2SZdNg/exec'

# Function to download the Excel file from Google Drive
def download_excel_from_drive():
    # Step 1: Get the file URL from the Google Apps Script
    response = requests.get(web_app_url)
    response.raise_for_status()  # Check for request errors
    file_url = response.text.strip()

    print(file_url)
    
    # Convert the file URL to a direct download link
    download_url = file_url.split("/edit")[0] + "/export?format=xlsx"

    # Download the file content
    file_response = requests.get(download_url)
    file_response.raise_for_status()  # Check for download errors
    
    # Load the Excel file into a pandas DataFrame
    excel_data = BytesIO(file_response.content)
    df = pd.read_excel(excel_data, sheet_name="Registration Dates")
    return df

# Load configuration settings
def load_config(config_path="C:/Users/ironk/Downloads/test gsheet/config.json"):
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

# Load user preferences
config = load_config()

# Load the Excel data directly from Google Drive
df = download_excel_from_drive()
df['Registration_Date'] = pd.to_datetime(df['Registration_Date'], format='%d/%m/%Y').dt.date

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

# Run scheduled tasks

while True:

    schedule.run_pending()  # Check if any reminder is due
    '''
    notification.notify(
            title=f"Reminder: No event",
            message=f"NIL",
            timeout=60  # Notification duration in seconds
        )'''
    time.sleep(30)  # Check every minute
    
    

