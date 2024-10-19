import os
import datetime
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.generativeai as genai
from dotenv import load_dotenv
from dateutil import parser, relativedelta

# Load env variables
load_dotenv()

# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/calendar', 'https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google_calendar():
    """Handles Google OAuth2 authentication and returns the service."""
    try:
        creds = None
        token_path = '/Users/aswath/Desktop/ethos/ethos/backend/components/calender_token.json'
        credentials_path = '/Users/aswath/Desktop/ethos/ethos/backend/components/calender_credentials.json'
        
        # Check if token.json exists
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
                creds = flow.run_local_server(port=8080)

            # Save the credentials for the next run
            with open(token_path, 'w') as token:
                token.write(creds.to_json())

        # Create service to interact with Google Calendar API
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"There was an issue during authentication: {e}")
        return None


def parse_natural_language(prompt: str):
    """Parse a natural language prompt into a structured command."""
    try:
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-pro')

        system_prompt = """
        Current date: Take today's date
        Parse the following natural language input into a structured JSON format.
        The JSON should include 'title', 'start_time', and 'end_time' (assumed to be 1 hour after start if not specified).
        Use the format "YYYY-MM-DDTHH:MM:SS" for times. Assume the current year if not specified.
        For relative time expressions like "tomorrow", "next week", etc., convert them to actual dates.
        Example input: "Add a meeting with John at 2pm tomorrow"
        Example output: {"title": "Meeting with John", "start_time": "2024-09-28T14:00:00", "end_time": "2024-09-28T15:00:00"}
        """

        response = model.generate_content(f"{system_prompt}\n\nInput: {prompt}")
        json_str = response.text.strip()
        if json_str.startswith('```json'):
            json_str = json_str[7:-3]

        result = json.loads(json_str)
        if "tomorrow" in prompt.lower():
            start_time = parser.parse(result['start_time']) + relativedelta.relativedelta(days=1)
            end_time = parser.parse(result['end_time']) + relativedelta.relativedelta(days=1)
            result['start_time'] = start_time.isoformat()
            result['end_time'] = end_time.isoformat()

        return result
    except json.JSONDecodeError:
        print("Error parsing JSON from model response.")
        return None
    except Exception as e:
        print(f"There was an issue parsing the input: {e}")
        return None


def create_event(service, title, start_time, end_time):
    """Creates an event in the Google Calendar."""
    try:
        event = {
            'summary': title,
            'start': {
                'dateTime': start_time,
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'Asia/Kolkata',
            },
        }
        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        print(f"There was an issue creating the event: {e}")
        return "There was an issue creating the event. Please try again later."


def get_upcoming_events(service, days=7):
    """Fetches upcoming events for the next specified number of days."""
    try:
        now = datetime.datetime.utcnow()
        time_min = now.isoformat() + 'Z'
        time_max = (now + datetime.timedelta(days=days)).isoformat() + 'Z'

        events_result = service.events().list(calendarId='primary', timeMin=time_min, timeMax=time_max,
                                              maxResults=10, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            return f'No upcoming events found for the next {days} days.'

        l = [f"{event['start'].get('dateTime', event['start'].get('date'))}: {event['summary']}\n\n" for event in events]
        return " ".join(l)
    except Exception as e:
        print(f"There was an issue fetching upcoming events: {e}")
        return "There was an issue fetching the events. Please try again later."


def schedule_calender(query):
    """Schedules or retrieves calendar events based on the query."""
    try:
        service = authenticate_google_calendar()
        if not service:
            return "Failed to authenticate Google Calendar. Please try again later."

        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        model = genai.GenerativeModel('gemini-1.5-pro')

        prompt_template3 = """
        The user gives {query}.
        Based on that you have to identify if the user wants to add an event or view upcoming events.
        1)If the user wants to add an event, return the prompt as it is.
        2)If the user wants to View Upcoming events, just return the number of days alone based on the user's query.

        Example of how the response should be:
        Sample Query: Schedule a meeting with Anand on Sunday
        Respond only: Schedule a meeting with Anand on Sunday

        Sample Query: Show me my events for the next 5 days
        Respond only: 5
        """

        prompt = prompt_template3.format(query=query)
        response = model.generate_content(prompt)
        text = response.text.strip()

        if len(text) >= 3:
            parsed_data = parse_natural_language(query)
            if parsed_data:
                return create_event(service, parsed_data['title'], parsed_data['start_time'], parsed_data['end_time'])
            else:
                return "Failed to parse the input. Please try again."
        else:
            days = int(text)
            return get_upcoming_events(service, days)

    except Exception as e:
        print(f"There was an issue processing the request: {e}")
        return "There was an issue processing your request. Please try again later."
