import pathlib
import datetime
import httplib2
from apiclient import discovery
from googleapiclient.http import MediaFileUpload
from credential import get_credential

MIME_TYPE = 'application/vnd.google-apps.document'
SCOPES = ['https://www.googleapis.com/auth/drive.file',
          'https://www.googleapis.com/auth/gmail.readonly']
DOC_SCOPES = 'https://www.googleapis.com/auth/documents.readonly'
DISCOVERY_DOC = ('https://docs.googleapis.com/$discovery/rest?'
                 'version=v1')
upload_dir = 'images'
client_secret = 'client_id.json'
application_name = 'Ryo-meshi'


def upload_with_ocr(upload_file_name):
    credentials = get_credential(application_name, client_secret, SCOPES)
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
    credential = get_credential(application_name, client_secret, SCOPES)
    service = discovery.build('docs', 'v1', http=credential.authorize(httplib2.Http()),
                              discoveryServiceUrl=DISCOVERY_DOC)
    result = service.documents().get(documentId=fid).execute()
    s = result['body']['content'][2]['paragraph']['elements'][0]['textRun']['content']
    s = s.replace('「', '')
    s = s.replace('」', '')
    s = s.replace('|', '')
    s = s.replace('.', '')
    menus = s.split(' ')

    return menus


def get_date(fid):
    credential = get_credential(application_name, client_secret, SCOPES)
    service = discovery.build('docs', 'v1', http=credential.authorize(httplib2.Http()),
                              discoveryServiceUrl=DISCOVERY_DOC)
    result = service.documents().get(documentId=fid).execute()
    s = result['body']['content'][2]['paragraph']['elements'][0]['textRun']['content']
    s = s.split('(')[0]
    s = s.replace('・', '')
    s = datetime.datetime.strptime(s, '%m月%d日').strftime('%m/%d')

    return s


def delete_docs(fid):
    credential = get_credential()
    service = discovery.build('drive', 'v3', http=credential.authorize(httplib2.Http()))
    service.files().delete(fileId=fid).execute()
