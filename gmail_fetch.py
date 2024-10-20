import os
import base64
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup  # For parsing HTML content
import re
from datetime import datetime
import pytz
from nltk.corpus import stopwords
# import spam_predictor
import random


# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def gmail_authenticate():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # Token file to store the access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                r'C:\Users\Pulkit Mangla\Documents\Machine Learning\WhatsApp Chat Analyzer\google_client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8000)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Build the Gmail service
    service = build('gmail', 'v1', credentials=creds)
    return service

def preprocess_text(text):
    # Remove HTML tags
    soup = BeautifulSoup(text, "html.parser")
    text = soup.get_text()
    
    # Remove URLs
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # Remove special characters and numbers
    text = re.sub(r'\W', ' ', text)
    text = re.sub(r'\d', ' ', text)
    
    # Lowercase
    text = text.lower()
    
    # Remove stopwords
    # stop_words = set(stopwords.words('english'))
    words = text.split()
    # words = [word for word in words if word not in stop_words]
    
    return ' '.join(words)

def convert_to_ist(date_str):
    # List of possible date formats
    possible_formats = [
        '%a, %d %b %Y %H:%M:%S %z',        # e.g., "Mon, 23 Sep 2024 14:30:12 +0000"
        '%a, %d %b %Y %H:%M:%S %Z',        # e.g., "Mon, 23 Sep 2024 14:30:12 UTC"
        '%a, %d %b %Y %H:%M:%S %z (%Z)'     # e.g., "Mon, 23 Sep 2024 14:30:12 +0000 UTC"
    ]
    
    for fmt in possible_formats:
        try:
            # Attempt to parse the date string with the current format
            email_date = datetime.strptime(date_str, fmt)
            
            # If the parsed datetime is naive, assume UTC
            if email_date.tzinfo is None:
                email_date = email_date.replace(tzinfo=pytz.UTC)
            
            # Convert to IST
            ist_zone = pytz.timezone('Asia/Kolkata')
            ist_date = email_date.astimezone(ist_zone)
            
            # Format the date in 12-hour format with AM/PM
            formatted_date = ist_date.strftime('%I:%M %p, %d-%b-%Y')
            return formatted_date
        
        except ValueError:
            continue  # Try the next format
    
    # If none of the formats match, return the original string
    return date_str

def fetch_emails(max_results=5, sender_email=None, start_date=None, end_date=None):
    service = gmail_authenticate()
    emails_data = []

    try:
        # Queries to fetch from inbox and spam
        queries = {
            'inbox': 'in:inbox',
            'spam': 'in:spam'
        }
        
        if sender_email:
            queries['inbox'] = f'from:{sender_email} in:inbox'
            queries['spam'] = f'from:{sender_email} in:spam'

        # Add date filters to the query if provided
        if start_date:
            queries['inbox'] += f' after:{start_date}'
            queries['spam'] += f' after:{start_date}'
        if end_date:
            queries['inbox'] += f' before:{end_date}'
            queries['spam'] += f' before:{end_date}'

        # Fetch inbox and spam messages separately
        inbox_emails = []
        spam_emails = []

        for label, query in queries.items():
            # Use the query parameter to search for emails
            results = service.users().messages().list(userId='me', maxResults=max_results, q=query).execute()
            messages = results.get('messages', [])
            
            if not messages:
                print(f'No messages found in {label}.')
                continue

            print(f'Found {len(messages)} messages in {label}:\n')

            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()

                # Extract headers
                headers = msg.get('payload', {}).get('headers', [])
                subject = next((header['value'] for header in headers if header['name'] == 'Subject'), 'No Subject')
                sender = next((header['value'] for header in headers if header['name'] == 'From'), 'Unknown Sender')
                date_str = next((header['value'] for header in headers if header['name'] == 'Date'), 'Unknown Date')
                
                # Convert date to IST and format
                formatted_date = convert_to_ist(date_str)

                # Initialize message string
                msg_str = ""
                links = []

                # Check if the message is multipart
                if 'parts' in msg['payload']:
                    parts = msg['payload']['parts']
                    for part in parts:
                        if part.get('filename'):
                            continue
                        mime_type = part.get('mimeType')
                        body = part.get('body', {})
                        data = body.get('data')

                        if mime_type == 'text/plain' and data:
                            # Decode plain text
                            decoded_data = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                            msg_str += decoded_data
                            break  # Prefer plain text over HTML
                        elif mime_type == 'text/html' and data:
                            # Decode HTML and extract text
                            decoded_data = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                            soup = BeautifulSoup(decoded_data, 'html.parser')
                            text = soup.get_text(separator='\n')
                            msg_str += text
                            # Extract links from the HTML content
                            links = [a['href'] for a in soup.find_all('a', href=True)]
                else:
                    # For non-multipart messages, decode the body directly
                    body = msg['payload']['body']
                    data = body.get('data')
                    if data:
                        decoded_data = base64.urlsafe_b64decode(data.encode('ASCII')).decode('utf-8')
                        msg_str += decoded_data

                # Clean up the message text
                clean_msg = preprocess_text(msg_str)

                # Extract links from the plain text using regex (if it's not HTML)
                if not links:
                    links = re.findall(r'(https?://\S+)', msg_str)

                # Set isSpam based on the label
                isSpam = 'YES' if label == 'spam' else 'NO'

                # Append the data to the appropriate list
                email_info = {
                    'TIME': formatted_date,
                    'FROM': sender,
                    'SUBJECT': subject,
                    'MESSAGE': clean_msg,
                    'SPAM': isSpam,
                    'LINKS': links
                }

                if isSpam == 'YES':
                    spam_emails.append(email_info)
                else:
                    inbox_emails.append(email_info)

        # Mixing spam and non-spam with 30-70% ratio
        total_emails = len(inbox_emails) + len(spam_emails)
        max_spam_emails = int(0.2 * total_emails)  # Max 30% spam
        mixed_emails = spam_emails[:max_spam_emails] + inbox_emails

        # Shuffle the emails randomly
        # random.shuffle(mixed_emails)

        # Limit the result to the maximum results requested by the user
        emails_data = mixed_emails[:max_results]

    except Exception as e:
        print(f"An error occurred while fetching emails: {e}")
    
    return emails_data
