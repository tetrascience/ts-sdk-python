import json
import requests
from datetime import datetime, timezone, timedelta
import time

class Command:

    def __init__(self, endpoint):
        self.endpoint = endpoint

    def run_command(self, context_data, org_slug, target_id, action, metadata, payload, ttl_sec):
        if org_slug is None:
            raise Exception('Param org_slug is missing')
        if target_id is None:
            raise Exception('Param target_id is missing')
        if action is None:
            raise Exception('Param action is missing')
        if payload is None:
            raise Exception('Param payload is missing')
        if ttl_sec < 300 or ttl_sec > 900:
            raise Exception('Param ttl_sec must be between 300 and 900 seconds')

        if metadata is None:
            metadata = {}

        metadata["workflowId"] = context_data.get("workflowId")
        metadata["pipelineId"] = context_data.get("pipelineId")
        metadata["taskId"] = context_data.get("taskId")

        url = self.endpoint + "/internal"
        date_now = datetime.now(timezone.utc) + timedelta(0, ttl_sec)

        command_create_payload = {
            "targetId": target_id,
            "action": action,
            "metadata": metadata,
            "expiresAt": date_now.isoformat(),
            "payload": payload
        }

        headers = { "x-org-slug": org_slug, "Content-Type": "application/json" }

        response = requests.request("POST", url, headers=headers, data=json.dumps(command_create_payload))
        if response.status_code == 200:
            print("Command successfully created")
            r = json.loads(response.text)
            command_id = r.get("id")

            command_url = self.endpoint + "/internal/" + command_id
            command_headers = { "x-org-slug": org_slug }

            time_elapsed = 0
            while time_elapsed <= ttl_sec:
                time.sleep(5)
                time_elapsed += 5
                command_response = requests.request("GET", command_url, headers=command_headers)
                print("Polling for command status")
                if command_response.status_code == 200:
                    command = json.loads(command_response.text)
                    command_status = command.get("status")
                    print('Current command status: ' + command_status)
                    if command_status == "SUCCESS":
                        return command.get("responseBody")
                    elif command_status == "CREATED" or command_status == "PENDING" or command_status == "PROCESSING":
                        continue
                    else:
                        raise Exception("Command status is " + command_status)

            if time_elapsed >= ttl_sec:
                print('TTL for command has expired')
                raise Exception("Command TTL has expired")
        else:
            print('Error creating command: ' + response.text)
            raise Exception(response.text)


        return response

