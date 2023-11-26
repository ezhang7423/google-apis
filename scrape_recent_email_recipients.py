import os.path
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
from rich import print

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def extract_name_email(recipient):
    # Regular expression to extract name and email from the recipient string
    pattern = r'(?:"?([^"]*)"?\s)?(?:<?(.+?@[^>,]+)>?)'
    matches = re.finditer(pattern, recipient)
    extracted_recipients = []  # A list to contain tuples of (name, email) pairs

    for match in matches:
        name = match.group(1)
        email = match.group(2)

        # Some cleanup to remove enclosing quotes if present
        if name:
            name = name.strip('"')

        extracted_recipients.append((name, email))

    return extracted_recipients

def get_recent_email_recipients(service, save_to_folder=True):
    response = service.users().messages().list(userId='me', q='in:sent').execute()
    messages = response.get('messages', [])
    recipients = set()

    for message in messages:
        msg_id = message['id']
        message_detail = service.users().messages().get(userId='me', id=msg_id).execute()
        headers = message_detail.get('payload', {}).get('headers', [])
        for header in headers:
            if header.get('name') == 'To':
                recipient_list = extract_name_email(header.get('value'))
                for name, email in recipient_list:
                    formatted_name = name if name else email.split('@')[0].replace('.', '_').replace(' ', '_')
                    recipients.add((formatted_name, email))

    print(recipients)
    
    # TODO clean this data  better. maybe we use gpt here...

    
    # recipients = set()
    # for name in rl:
    #     recipient_list = extract_name_email(name)
    #     for name, email in recipient_list:
    #         formatted_name = name if name else email.split('@')[0].replace('.', '_').replace(' ', '_')
    #         recipients.add((formatted_name, email))
    # print(recipients)
    if save_to_folder:
        folder_name = "recipients"
        os.makedirs(folder_name, exist_ok=True)

        for name, email in recipients:
            email_extension = email.split('@')[-1]
            file_name = f"{name}.md"

            with open(os.path.join(folder_name, file_name), 'w') as file:
                file.write(f'#{email_extension}\n')

    return recipients

def main():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    service = build("gmail", "v1", credentials=creds)
    get_recent_email_recipients(service)    
    

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
