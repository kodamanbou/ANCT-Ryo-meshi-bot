import httplib2
from apiclient import discovery
from credential import get_credential

SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.labels",
    "https://www.googleapis.com/auth/gmail.modify",
]
application_name = 'Ryo-meshi'
client_secret = 'client_id.json'
save_dir = 'data'


if __name__ == '__main__':
    creds = get_credential(application_name, client_secret, SCOPES)
    http = creds.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
