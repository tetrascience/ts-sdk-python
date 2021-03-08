import json
import requests

class Fileinfo:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def add_labels(self, context_data, file_id, labels):

        org_slug = context_data.get('orgSlug')
        url = f'{self.endpoint}/internal/{org_slug}/files/{file_id}/labels'

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request('POST', url, headers=headers, data=json.dumps(labels), verify=False)

        if response.status_code == 200:
            print('Labels successfully added')
            return json.loads(response.text)
        else:
            print('Error adding labels: ' + response.text)
            raise Exception(response.text)

    def get_labels(self, context_data, file_id):
        org_slug = context_data.get('orgSlug')
        url = f'{self.endpoint}/internal/{org_slug}/files/{file_id}/labels'
        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request('GET', url, headers=headers, verify=False)

        if response.status_code == 200:
            print('Labels successfully obtained')
            return json.loads(response.text)
        else:
            print('Error getting labels: ' + response.text)
            raise Exception(response.text)

    def delete_labels(self, context_data, file_id, label_ids):
        if label_ids is None or len(label_ids) == 0:
            print('Empty labels_ids')
            return
        org_slug = context_data.get('orgSlug')

        if len(label_ids) == 1:
            suffix = f'id={label_ids[0]}&id={label_ids[0]}'
        else:
            suffix = '&'.join(map(lambda id: 'id=' + str(id), label_ids))
        url = f'{self.endpoint}/internal/{org_slug}/files/{file_id}/labels?{suffix}'

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request('DELETE', url, headers=headers, verify=False)

        if response.status_code == 200:
            print('Labels successfully deleted')
            return
        else:
            print('Error deleting labels: ' + response.text)
            raise Exception(response.text)
