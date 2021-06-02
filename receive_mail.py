import os
import httplib2
from apiclient import discovery
from credential import get_credential

SCOPES = ['https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/gmail.readonly']
client_secret = 'client_id.json'
application_name = 'Ryo-meshi'

if __name__ == '__main__':
    creds = get_credential(application_name, client_secret, SCOPES)
    http = creds.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    responce = service.users().labels().list(userId='me').execute()
    labels = responce['labels']
    target_label_ids = [label['id'] for label in labels if label['id'] == 'UNREAD']

    message_ids = (
        service.users().messages().list(userId='me', maxResults=100, q='is:unread',
                                        labelIds=target_label_ids).execute())

    if message_ids["resultSizeEstimate"] > 0:
        for message_id in message_ids['messages']:
            detail = (service.users().messages().get(userId='me', id=message_id['id']).execute())
            message = dict()
            message['from'] = [header['value']
                               for header in detail['payload']['headers']
                               if header['name'] == 'From'][0]
            print(message['from'])
    else:
        print('There are no messages.')
