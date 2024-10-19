import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import google.generativeai as genai
from datetime import datetime, timedelta
import json
import pytz
from dotenv import load_dotenv
load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

#Will be integrated with contacts to access mail ID'S
#For testing purposes, give name and mail ID
mail_dict={'aswath':'aswath2111001@ssn.edu.in','Aswath':'aswath2111001@ssn.edu.in','team': ['aswath2111001@ssn.edu.in', 'aswathvenkateshofficial@gmail.com'],'team': ['aswath2111001@ssn.edu.in', 'aswathvenkateshofficial@gmail.com']}

#prompt to identify whether to send or retreive mail
prompt_template3 = """
You are an assistant that helps the user to send mails or access mails from gmail
{query} is what the user has provided. 
From this we have to identify if the user has to send a mail or retreive a mail.
1)If the user want to send a mail, then return the name of the person user wants to send along with content
2)If the user wants to retreive a mail, return the prompt as it is

Response(Prompt as it is for retreival else name in first line and content in second line alone):
"""

# Define the scopes for accessing Gmail
SCOPES = ['https://www.googleapis.com/auth/gmail.modify', 'https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Handles Google OAuth2 authentication and returns the Gmail service."""
    creds = None
    # if os.path.exists('/path/to/token.json'): #will be created if it does not exist
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        # creds = Credentials.from_authorized_user_file('/path/to/token.json', SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # flow = InstalledAppFlow.from_client_secrets_file('path/to/gmail_credentials.json', SCOPES) #Check readme.md on how to obtain
            flow = InstalledAppFlow.from_client_secrets_file('/Users/aswath/Desktop/ethos/ethos/backend/components/gmail.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.json', 'w') as token:
        # with open('/path/to/token.json', 'w') as token:
            token.write(creds.to_json())
    
    try:
        service = build('gmail', 'v1', credentials=creds)
        # Test the connection
        service.users().getProfile(userId='me').execute()
        return service
    except Exception as e:
        # print(f"Error authenticating with Gmail: {e}")
        return None

def create_message_content(prompt):
    """Use Gemini to create email subject and content."""

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))  # Replace with your actual API key
    model = genai.GenerativeModel('gemini-1.5-pro')


    #Identify Subject and content

    system_prompt = f"""
    Based on the following context, create a natural, professional email subject and content:

    Context: {prompt}

    Requirements:
    1. Subject: Create a brief, specific subject line directly related to the email's purpose.
    2. Content: Write a professional email body that addresses the context provided.
    3. Style: Use a natural, conversational tone appropriate for professional communication.
    4. Personalization: Use the recipient's name and include specific details from the context (e.g., "final project review"). Dont use [brackets]
    5. Avoid: Do not use placeholder text such as brackets (e.g., "[Recipient Name]" or "[briefly mention]"). Instead, directly refer to the content.
    6. Signature: Always sign the email with "Aswath Venkatesh."
    7. Format: Respond with a JSON object containing 'subject' and 'content' keys.


    Remember you are sending the mail on behalf of me but it should look like I am sending the mail. So don't use [] anywhere
    
    Example format:
    {{
      "subject": "Great news from the project review!",
      "content": "Hi Aswath,\\n\\nI just wanted to let you know that I had my final project review today, and it went really well! I'm feeling quite relieved.\\n\\nAlso, how's your mom doing? I hope she's feeling better.\\n\\nBest regards,\\nAswath Venkatesh"
    }}
    """


    
    try:
        response = model.generate_content(system_prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        result = json.loads(cleaned_response)
        return result['subject'], result['content']

    except json.JSONDecodeError as e:
        # print(f"Error parsing JSON: {e}")
        # print(f"Raw response: {response.text}")
        lines = response.text.split('\n')
        subject = next((line.split(': ', 1)[1] for line in lines if line.startswith('"subject":')), "Meeting Follow-up")
        content = prompt
        return subject, content

    except KeyError as e:
        # print(f"Error: Missing key in generated content: {e}")
        return "Meeting Follow-up", prompt

    except Exception as e:
        # print(f"Error using Gemini API: {e}")
        return "Meeting Follow-up", prompt

# def send_email(service, to, subject, content):
#     #Send an email using the Gmail API.
#     if not service:
#         # print("Gmail service is not initialized. Cannot send email.")
#         return None

#     message = MIMEText(content)
#     message['to'] = to
#     message['subject'] = subject
#     raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
#     try:
#         message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
#         # print(f"Message Id: {message['id']}")
#         return message
#     except Exception as e:
#         # print(f"An error occurred while sending the email: {e}")
#         return None

def send_email(service, to, subject, content):
    """Send an email using the Gmail API, supporting both single recipients and groups."""
    if not service:
        return "Gmail service is not initialized. Cannot send email."

    # Ensure 'to' is always a list
    if isinstance(to, str):
        to = [to]

    message = MIMEText(content)
    message['to'] = ', '.join(to)  # Join multiple recipients with commas
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    try:
        message = service.users().messages().send(userId='me', body={'raw': raw_message}).execute()
        return f"Message sent successfully. Message Id: {message['id']}"
    except Exception as e:
        return f"An error occurred while sending the email: {str(e)}"

def process_email_query(query):
    #Process natural language email retrieval queries.

    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    system_prompt = f"""
    Convert the following natural language query into a structured JSON format for email retrieval:
    Query: {query}
    Include 'time_range' (e.g., 'today', 'this_week', 'last_7_days', or null if not specified),
    'importance' (boolean),
    'keywords' (list),
    'read' (boolean or null if not specified),
    'sender' (string or null if not specified),
    'limit' (number or null if not specified).
    Example output: {{"time_range": "today", "importance": false, "keywords": [], "read": null, "sender": null, "limit": 5}}
    """
    
    try:
        response = model.generate_content(system_prompt)
        # print(f"Response from Gemini: {response.text}")
        
        json_str = response.text.strip()
        if json_str.startswith('```json'):
            json_str = json_str[7:-3]  # Remove ```json and ``` 
        
        result = json.loads(json_str)
        return result
    except Exception as e:
        # print(f"Error processing query with Gemini: {e}")
        return {"time_range": None, "importance": False, "keywords": [], "read": None, "sender": None, "limit": 5}

def get_emails(service, query_params):
    """Retrieve emails based on the processed query parameters."""
    if not service:
        # print("Gmail service is not initialized. Cannot retrieve emails.")
        return "Gmail service is not initialized. Cannot retrieve emails."

    try:
        now = datetime.now(pytz.utc)
        time_range = query_params.get('time_range')
        
        query = ''
        
        if time_range:
            if time_range == 'today':
                after = now.replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == 'yesterday':
                after = (now - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == 'this_week':
                after = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            elif time_range == 'last_7_days':
                after = now - timedelta(days=7)
            else:
                after = now - timedelta(days=30)  # Default to last 30 days
            
            after_str = after.strftime('%Y-%m-%dT%H:%M:%SZ')
            query += f'after:{after_str} '

        if query_params.get('importance', False):
            query += 'is:important '
        
        read_status = query_params.get('read')
        if read_status is not None:
            query += 'is:unread ' if not read_status else 'is:read '
        
        sender = query_params.get('sender')
        if sender:
            query += f'from:{sender} '
        
        keywords = query_params.get('keywords', [])
        if keywords:
            query += '(' + ' OR '.join(keywords) + ') '

        query = query.strip()
        # print(f"Executing Gmail API query: {query}")
        # print(f"Current UTC time: {now.strftime('%Y-%m-%dT%H:%M:%SZ')}")

        all_results = service.users().messages().list(userId='me', maxResults=5).execute()
        all_messages = all_results.get('messages', [])
        
        if not all_messages:
            print("No messages found in the inbox at all. This might indicate an authentication or permission issue.")
            return "No messages found in the inbox at all. This might indicate an authentication or permission issue."
        else:
            print(f"Found {len(all_messages)} messages in the inbox without any query.")
            # return f"Found {len(all_messages)} messages in the inbox without any query."

        # Now execute the actual query
        results = service.users().messages().list(userId='me', q=query, maxResults=query_params.get('limit', 5)).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found matching the query.')
            return 'No messages found matching the query.'

        # print(f'Found {len(messages)} messages matching the query:')
        l=[]
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            headers = msg['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'].lower() == 'date'), 'Unknown Date')
            # print(f"Date: {date}")
            # print(f"Subject: {subject}")
            # print(f"From: {sender}")
            # print(f"Snippet: {msg['snippet']}")
            l.append(f"Date: {date}\nSubject: {subject}\nFrom: {sender}\nSnippet: {msg['snippet']}\n\n")
            
        return("\n".join(l))

    except Exception as e:
        print(f"An error occurred while retrieving emails: {e}")
        return f"An error occurred while retrieving emails: {e}"

# def call_mail(query):
#     service = authenticate_gmail()
#     if not service:
#         print("Failed to authenticate with Gmail. Exiting.")
#         return
#     prompt = prompt_template3.format(query=query)
#     response = model.generate_content(prompt)    
#     # print(response.text)
#     lines = response.text.splitlines()
#     if len(lines)>1:
#         name = lines[0]  
#         unformated_content = lines[1] 
#         to=mail_dict[name]
#         subject, content = create_message_content(unformated_content)
#         # print(f"\nGenerated Subject: {subject}")
#         # print(f"Generated Content: {content}")
#         send_email(service, to, subject, content)
#         return f"Mail has been sent successfully\nSubject: {subject}\nBody: {content}"
#     else:
#         query_params = process_email_query(lines[0])
#         return get_emails(service, query_params)

def call_mail(query):
    try:
        service = authenticate_gmail()
        if not service:
            return "Failed to authenticate with Gmail. Exiting."
        
        prompt = prompt_template3.format(query=query)
        response = model.generate_content(prompt)    
        lines = response.text.splitlines()
        
        if len(lines) > 1:
            name = lines[0].strip()
            print('\n1', name, '1\n')
            unformatted_content = lines[1] 
            
            try:
                to = mail_dict[name]
            except KeyError:
                print(f"Contact '{name}' not found in the mail dictionary.")
                return f"Contact '{name}' not found in the mail dictionary."
            
            subject, content = create_message_content(unformatted_content)
            
            result = send_email(service, to, subject, content)
            
            if "successfully" in result:
                if isinstance(to, list):
                    recipients = ', '.join(to)
                    return f"Mail has been sent successfully to the group: {recipients}\nSubject: {subject}\nBody: {content}"
                else:
                    return f"Mail has been sent successfully to: {to}\nSubject: {subject}\nBody: {content}"
            else:
                return result  # This will be the error message from send_email
        else:
            query_params = process_email_query(lines[0])
            return get_emails(service, query_params)
    except Exception as e:
        print(f"Error occurred: {e}")  # You can log the error for debugging purposes
        return "Error processing request."


    
