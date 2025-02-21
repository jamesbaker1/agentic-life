import os
import pickle
import base64
from datetime import datetime, timedelta
from email import message_from_bytes
from email.mime.text import MIMEText

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Import the OpenRouter API client (using the OpenAI package interface)
from openai import OpenAI

# --- Configuration ---

# Set up the OpenRouter API client.
# Environment variable OPENROUTER_API_KEY must be set.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
YOUR_SITE_URL = os.environ.get("YOUR_SITE_URL", "https://example.com")
YOUR_SITE_NAME = os.environ.get("YOUR_SITE_NAME", "MySite")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

OPENROUTER_HEADERS = {
    "HTTP-Referer": YOUR_SITE_URL,
    "X-Title": YOUR_SITE_NAME,
}

# The Gmail scopes for reading and sending mail.
SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.send'
]

# --- Gmail API Helper Functions ---

def get_gmail_service():
    """
    Authenticate and create a Gmail API service instance.
    Expects that 'credentials.json' and 'token.pickle' are available.
    """
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no valid credentials, the script would normally initiate an OAuth flow.
    # In GitHub Actions, you must pre‑provide a valid token.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            raise Exception("No valid credentials available. You must pre‑authenticate and store token.pickle.")
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_emails(service):
    """
    Retrieve email messages from the last 12 hours using the Gmail search query.
    """
    # The Gmail search operator "newer_than:12h" finds messages received within the last 12 hours.
    results = service.users().messages().list(userId='me', q="newer_than:12h").execute()
    messages = results.get('messages', [])
    return messages

def get_email_content(service, msg_id):
    """
    Fetch and decode the plain-text content from an email.
    """
    message = service.users().messages().get(userId='me', id=msg_id, format='raw').execute()
    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mime_msg = message_from_bytes(msg_str)
    body = ""
    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/plain':
                part_payload = part.get_payload(decode=True)
                if part_payload:
                    body += part_payload.decode('utf-8', errors='ignore')
    else:
        payload = mime_msg.get_payload(decode=True)
        if payload:
            body = payload.decode('utf-8', errors='ignore')
    return body

def send_email(service, to_email, subject, message_text):
    """
    Send an email using the Gmail API.
    """
    message = MIMEText(message_text)
    message['to'] = to_email
    message['from'] = "me"
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
    message_body = {'raw': raw_message}
    sent_message = service.users().messages().send(userId="me", body=message_body).execute()
    return sent_message

# --- OpenRouter API Function ---

def generate_todo_list(email_content):
    """
    Use the OpenRouter API to extract actionable todo items from the email content.
    The prompt instructs the model to list actionable items.
    """
    prompt = f"""Extract a list of actionable todo items from the following email content:

{email_content}

Todo list:"""
    response = client.chat.completions.create(
        extra_headers=OPENROUTER_HEADERS,
        extra_body={},
        model="perplexity/r1-1776",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    todo_items = response.choices[0].message.content.strip()
    return todo_items

# --- Main Process ---

def main():
    service = get_gmail_service()
    emails = get_emails(service)
    if not emails:
        print("No emails found in the last 12 hours.")
        return

    aggregated_todo = []  # List to accumulate todo items from each email

    for email in emails:
        msg_id = email['id']
        print(f"Processing email ID: {msg_id}")
        content = get_email_content(service, msg_id)
        if not content.strip():
            continue

        # Generate todo items using OpenRouter API
        todo = generate_todo_list(content)
        if todo:
            aggregated_todo.append(f"Email ID {msg_id}:\n{todo}\n")

    # If any actionable todo items were found, send an aggregated email.
    if aggregated_todo:
        aggregated_text = "\n".join(aggregated_todo)
        subject = "Aggregated Todo List Items from the Past 12 Hours"
        recipient = "jamesbaker2019@gmail.com"
        send_email(service, recipient, subject, aggregated_text)
        print("Sent aggregated todo list email.")
    else:
        print("No actionable todo items found; no email sent.")

if __name__ == '__main__':
    main()
