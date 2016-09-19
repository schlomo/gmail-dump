import base64

import httplib2
import os
import base64
import email
import mailbox

from googleapiclient.http import BatchHttpRequest
from googleapiclient import discovery, errors
import oauth2client
from oauth2client import file
from oauth2client import client
from oauth2client import tools

try:
    import argparse

    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/gmail-dump.json
SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CLIENT_SECRET_FILE = 'client_secrets.json'
APPLICATION_NAME = 'GMail Dump'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-dump.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else:  # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """
    GMail Dump
    * Get & Store credentials
    * Download all GMail messages into Maildir folder named mail
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    profile = service.users().getProfile(userId='me').execute()
    # example: {'historyId': '380957', 'emailAddress': 'user@domain', 'threadsTotal': 1135, 'messagesTotal': 1950}
    print("Downloading {messagesTotal} messages for {emailAddress}".format(**profile))

    box = mailbox.Maildir('mail', create=True)
    box.lock()

    def process_message(request_id, response, exception):
        if exception is not None:
            print("ERROR: " + request_id)
        else:
            msg_bytes = base64.urlsafe_b64decode(response['raw'].encode('ASCII'))
            mime_msg = email.message_from_bytes(msg_bytes)
            maildir_message = mailbox.MaildirMessage(mime_msg)
            #box.add(maildir_message)
            with open("mail/cur/%s" % response['id'], "wb") as message_file:
                message_file.write(maildir_message.__bytes__())

    try:
        message_count = 0
        start = True
        while start or 'nextPageToken' in response:
            if start:
                page_token = None
                start = False
            else:
                page_token = response['nextPageToken']
            response = service.users().messages().list(userId='me', pageToken=page_token).execute()
            if 'messages' in response:
                message_count += len(response['messages'])
                batch = BatchHttpRequest(callback=process_message)
                for message in response['messages']:
                    batch.add(service.users().messages().get(userId='me', format='raw', id=message['id']))
                batch.execute()
                print("Downloaded %s messages" % message_count)
    except errors.HttpError as error:
        print('An HTTPError occurred: %s' % error)

    box.unlock()
    box.close()


if __name__ == '__main__':
    main()
