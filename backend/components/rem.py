import re
import os
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import socket

SCOPES = ['https://www.googleapis.com/auth/tasks']
REDIRECT_URI = 'http://localhost:8080/'

class GoogleTasksReminder:
    def __init__(self):
        self.creds = None
        self.service = None
        self.authenticate()

    def authenticate(self):
        if os.path.exists('rem_token.json'):
            try:
                self.creds = Credentials.from_authorized_user_file('rem_token.json', SCOPES)
            except ValueError:
                self.creds = None

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    self.creds = None

            if not self.creds:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'rem_credentials.json',
                    SCOPES,
                    redirect_uri=REDIRECT_URI
                )
                
                port = self.find_available_port(8080, 8090)
                
                try:
                    self.creds = flow.run_local_server(
                        port=port,
                        authorization_prompt_message='Please visit this URL to authorize this application: {url}',
                        success_message='The auth flow completed successfully.',
                        open_browser=True
                    )
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return

            with open('rem_token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('tasks', 'v1', credentials=self.creds)

    def find_available_port(self, start_port, end_port):
        for port in range(start_port, end_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(('localhost', port))
                    return port
                except OSError:
                    continue
        raise OSError("No available ports found in the specified range.")

    def add_event(self, title, description, due_date, priority):
        task = {
            'title': f"[{priority.upper()}] {title}",
            'notes': description,
            'due': due_date.isoformat() + 'Z'
        }
        result = self.service.tasks().insert(tasklist='@default', body=task).execute()
        return result['id']

    def list_reminders(self, priority=None):
        try:
            tasks = self.service.tasks().list(tasklist='@default').execute().get('items', [])
            if priority:
                tasks = [task for task in tasks if task['title'].startswith(f'[{priority.upper()}]')]
            return tasks
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []

def extract_details_from_query(query):
    # Check if the query is for listing reminders
    if query.lower().startswith('list reminders'):
        priority_pattern = r'\b(low|medium|high)\b'
        priority_match = re.search(priority_pattern, query, re.IGNORECASE)
        priority = priority_match.group(0).lower() if priority_match else None
        return {
            "action": "list_reminders",
            "priority": priority
        }

    # Set default priority to 'low' if not specified
    priority_pattern = r'\b(low|medium|high)\b'
    priority_match = re.search(priority_pattern, query, re.IGNORECASE)
    priority = priority_match.group(0).lower() if priority_match else 'low'

    # Extract the due date (supports today, tomorrow, next week, etc.)
    date_pattern = r'\b(?:\d{4}-\d{2}-\d{2})|\btomorrow\b|\btoday\b|\bnext week\b|\b(?:\d{1,2}(?:am|pm))\b'
    date_match = re.search(date_pattern, query, re.IGNORECASE)
    if date_match:
        if date_match.group(0).lower() == 'tomorrow':
            due_date = datetime.datetime.now() + datetime.timedelta(days=1)
        elif date_match.group(0).lower() == 'today':
            due_date = datetime.datetime.now()
        elif date_match.group(0).lower() == 'next week':
            due_date = datetime.datetime.now() + datetime.timedelta(weeks=1)
        elif re.match(r'\d{1,2}(?:am|pm)', date_match.group(0), re.IGNORECASE):
            due_date = datetime.datetime.combine(datetime.datetime.now(), datetime.datetime.strptime(date_match.group(0), '%I%p').time())
        else:
            due_date = datetime.datetime.strptime(date_match.group(0), "%Y-%m-%d")
    else:
        due_date = datetime.datetime.now() + datetime.timedelta(days=1)

    # Updated title extraction logic
    # This extracts a clear action based on natural language patterns
    title_pattern = r'(?:set a reminder to|remind me to|i want to|add a reminder to|remind me about|create a reminder for)(.*?)(?:tomorrow|at|\bon|\bby|due)'
    title_match = re.search(title_pattern, query, re.IGNORECASE)
    title = title_match.group(1).strip() if title_match else query.strip()

    return {
        "action": "add_reminder",
        "title": title,
        "priority": priority,
        "due_date": due_date
    }


def schedule_reminder(query):
    reminder = GoogleTasksReminder()        
    details = extract_details_from_query(query)
    
    if details['action'] == 'add_reminder':
        title = details['title']
        priority = details['priority']
        due_date = details['due_date']

        l=[]
        
        l.append(f"\nSetting reminder with the following details:\n\n")
        l.append(f"Title: {title}\n")
        l.append(f"Priority: {priority}\n")
        l.append(f"Due Date: {due_date}\n")
        
        event_id = reminder.add_event(title, "Automatically created reminder", due_date, priority)
        
        if event_id:
            return "".join(l) + f"Reminder set successfully! Event ID: {event_id}"
        else:
            return "Failed to set reminder."

    elif details['action'] == 'list_reminders':
        priority = details['priority']
        l=[]
        if priority:
            l.append(f"Listing reminders with {priority} priority: \n\n")
        else:
            l.append("Listing all reminders: \n\n")
        
        tasks = reminder.list_reminders(priority)
        for task in tasks:
            l.append(f"Title: {task['title']}, Due: {task['due']}\n\n")
        return " ".join(l)
    else:
        return "Invalid query. Please try again."


if __name__ == "__main__":
    # print(schedule_reminder("set a reminder of medium priority to buy groceries due on 18th october 9pm"))
    print(schedule_reminder("list reminders"))
    print(schedule_reminder("list reminders with high priority"))
    # print(schedule_reminder("i want to buy medicine tomorrow..crate a reminder for that "))
    # print(schedule_reminder("i want to buy groceres tomorrow..create a medium priority reminder for that"))
