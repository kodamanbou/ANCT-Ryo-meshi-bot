import os
import argparse
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage


def get_credential(app_name, client_secret, scopes):
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        flow = client.flow_from_clientsecrets(client_secret, scopes)
        flow.user_agent = app_name
        credentials = tools.run_flow(flow, store, flags)
        print('Storing credentials to ' + credential_path)

    return credentials
