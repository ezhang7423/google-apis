import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


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
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().labels().list(userId="me").execute()
    labels = results.get("labels", [])

    if not labels:
      print("No labels found.")
      return
    print("Labels:")
    for label in labels:
      print(label["name"])

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()
  
# from googleapiclient.discovery import build
# from google.oauth2.credentials import Credentials
# from datetime import datetime, timedelta

# # Load your credentials (probably from a file or a database)
# # These credentials should be generated through the OAuth 2.0 flow.
# credentials = Credentials.from_authorized_user_file('credentials.json')

# # Build the Gmail service
# service = build('gmail', 'v1', credentials=credentials)

# # Calculate the date one month ago in RFC 3339 format
# one_month_ago = datetime.now() - timedelta(days=30)
# one_month_ago_rfc3339 = one_month_ago.isoformat() + 'Z'  # 'Z' indicates UTC time

# # List messages sent in the last month
# response = service.users().messages().list(
#     userId='me',
#     q='in:sent after:{}'.format(one_month_ago_rfc3339)
# ).execute()

# # Retrieve a list of Message IDs from the response
# messages = response.get('messages', [])

# # Extract recipients from these messages
# recipients = set()
# for message in messages:
#     msg_id = message['id']
#     message_detail = service.users().messages().get(userId='me', id=msg_id).execute()
#     headers = message_detail.get('payload', {}).get('headers', [])
#     for header in headers:
#         if header.get('name') == 'To':
#             recipient = header.get('value')
#             recipients.add(recipient)

# # Now `recipients` has all the unique email addresses you sent emails to in the last month.
# print(recipients)