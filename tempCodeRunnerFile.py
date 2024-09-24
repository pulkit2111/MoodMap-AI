def fetch_emails(service, max_results=5):
    # Call the Gmail API
    results = service.users().messages().list(userId='me', maxResults=max_results).execute()
    messages = results.get('messages', [])

    if not messages:
        print("No messages found.")
    else:
        print(f"Found {len(messages)} messages:")
        for message in messages:
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            msg_str = base64.urlsafe_b64decode(msg['payload']['body']['data'].encode('ASCII')).decode('utf-8')
            print(f"Message snippet: {msg['snippet']}")
            print(f"Full message: {msg_str}")

if __name__ == '__main__':
    service = gmail_authenticate()
    fetch_emails(service)
