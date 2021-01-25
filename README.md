# ts-sdk
Tetrascience Python SDK

## Install

```
pip3 install ts-sdk
```

## Usage

### Init a new protocol

```
ts-sdk init -o <org> -m <master-script-slug> -t <task-script-slug> -f <protocol-folder>
cd <protocol-folder>/task-script
pipenv install --dev
# task-script code modifications...
pipenv run pytest
```

### Upload artifact

```
export TS_ORG=<your-org-slug>
export TS_API_URL=https://api.tetrascience.com/v1
export TS_AUTH_TOKEN=<token>
ts-sdk put <ids|master-script|task-script> <namespace> <slug> <version> <artifact-folder>
```

## Dockerfile ENTRYPOINT

```
ENTRYPOINT [ "<python-bin>", "-u", "-m", "ts_sdk.task.run" ]
```
