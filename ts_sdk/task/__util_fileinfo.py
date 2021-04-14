import json
import requests
from time import sleep
from urllib.parse import urlencode

class Fileinfo:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def ensure_file_exists_in_db(self, file_id, org_slug, check_delay = 2, attempts_max = 10):
        url = f'{self.endpoint}/internal/{org_slug}/file-exists/{file_id}'
        headers = {
            'Content-Type': 'application/json'
        }
        attempt = 0
        while attempt < attempts_max:
            sleep(check_delay)
            response = requests.request('GET', url, headers=headers, verify=False)
            if response.status_code == 200:
                return True
            attempt = attempt + 1
        print({ 'level': 'error', 'message': 'File existence check failed' })
        return False

    def add_labels(self, context_data, file_id, labels, no_propagate = False):
        org_slug = context_data.get('orgSlug')
        self.ensure_file_exists_in_db(file_id, org_slug)

        query_str = urlencode({'noPropagate': 'true'} if no_propagate else {})
        url = f'{self.endpoint}/internal/{org_slug}/files/{file_id}/labels?{query_str}'

        headers = {
            'Content-Type': 'application/json',
            'x-pipeline-id': context_data.get('pipelineId')
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
        self.ensure_file_exists_in_db(file_id, org_slug)

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
        org_slug = context_data.get('orgSlug')
        self.ensure_file_exists_in_db(file_id, org_slug)

        suffix = '&'.join(map(lambda id: 'id=' + str(id), label_ids))
        url = f'{self.endpoint}/internal/{org_slug}/files/{file_id}/labels?{suffix}'

        headers = {
            'Content-Type': 'application/json',
            'x-pipeline-id': context_data.get('pipelineId')
        }
        response = requests.request('DELETE', url, headers=headers, verify=False)

        if response.status_code == 200:
            print('Labels successfully deleted')
            return
        else:
            print('Error deleting labels: ' + response.text)
            raise Exception(response.text)
