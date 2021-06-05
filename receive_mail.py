import base64
import httplib2
from apiclient import discovery
from credential import get_credential
from tweet.key import TARGET_ADDRESS

if __name__ == '__main__':
    creds = get_credential()
    http = creds.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    response = service.users().labels().list(userId='me').execute()
    labels = response['labels']
    target_label_ids = [label['id'] for label in labels if label['id'] == 'UNREAD']

    message_ids = (
        service.users().messages().list(userId='me', maxResults=100, q='is:unread',
                                        labelIds=target_label_ids).execute())

    if message_ids["resultSizeEstimate"] > 0:
        remove_ids = []
        for message_id in message_ids['messages']:
            message_detail = (service.users().messages().get(userId='me', id=message_id['id']).execute())
            message = dict()
            message['id'] = message_id['id']
            message['from'] = [header['value']
                               for header in message_detail['payload']['headers']
                               if header['name'] == 'From'][0]
            if message['from'].split('<')[1].strip('>') == TARGET_ADDRESS:
                attach_id = message_detail['payload']['parts'][1]['body']['attachmentId']
                response = service.users().messages().attachments().get(
                    userId='me',
                    messageId=message['id'],
                    id=attach_id
                ).execute()

                file_data = base64.urlsafe_b64decode(response.get('data').encode('UTF-8'))
                with open('data/data.pdf', 'wb') as f:
                    f.write(file_data)

                remove_ids.append(message['id'])

        if len(remove_ids) > 0:
            labels_mod = {
                'ids': remove_ids,
                'removeLabelIds': target_label_ids,
                'addLabelIds': []
            }

            message_ids = (
                service.users().messages().batchModify(
                    userId='me',
                    body=labels_mod
                ).execute()
            )
    else:
        print('There are no messages.')
