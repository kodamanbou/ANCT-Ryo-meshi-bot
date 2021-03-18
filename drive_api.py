import os
import argparse
import pathlib
import httplib2
from apiclient import discovery
from googleapiclient.http import MediaFileUpload
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

MIME_TYPE = 'application/vnd.google-apps.document'
SCOPES = 'https://www.googleapis.com/auth/drive.file'
DOC_SCOPES = 'https://www.googleapis.com/auth/documents.readonly'
DISCOVERY_DOC = ('https://docs.googleapis.com/$discovery/rest?'
                 'version=v1')
upload_dir = 'images'
client_secret = 'client_id.json'
application_name = 'Ryo-meshi'
flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()


def get_credential():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(client_secret, SCOPES)
        flow.user_agent = application_name
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)

    return credentials


def upload_with_ocr(upload_file_name):
    credentials = get_credential()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    local_file_path = pathlib.Path(__file__).resolve().parent.joinpath(upload_dir).joinpath(upload_file_name)
    media_body = MediaFileUpload(local_file_path, mimetype=MIME_TYPE, resumable=True)

    body = {
        'name': local_file_path.name,
        'mimeType': MIME_TYPE,
    }

    file = service.files().create(
        body=body,
        media_body=media_body,
        ocrLanguage='ja',
    ).execute()
    fid = file.get('id')

    return fid


def get_menu_items(fid):
    credential = get_credential()
    service = discovery.build('docs', 'v1', http=credential.authorize(httplib2.Http()),
                              discoveryServiceUrl=DISCOVERY_DOC)
    result = service.documents().get(documentId=fid).execute()
    s = result['body']['content'][2]['paragraph']['elements'][0]['textRun']['content']
    s = s.replace('「', '')
    s = s.replace('」', '')
    s = s.replace('|', '')
    s = s.replace('.', '')

    return s


def delete_docs(fid):
    credential = get_credential()
    service = discovery.build('drive', 'v3', http=credential.authorize(httplib2.Http()))
    service.files().delete(fileId=fid).execute()
