# ts-sdk
Tetrascience Python SDK

## Install

```
pip3 install ts-sdk
```

## Usage

### Init a new protocol

```
ts-sdk init -o <org> -p <protocol-slug> -t <task-script-slug> -f <protocol-folder>
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
ts-sdk put <ids|protocol|task-script> <namespace> <slug> <version> <artifact-folder>
```

It's also possible to use the configuration JSON file (`cfg.json`):
```
{
    "api_url": "https://api.tetrascience.com/v1",
    "auth_token": "your-token",
    "org": "your-org",
    "ignore_ssl": false
}
```
Usage: `ts-sdk put <ids|protocol|task-script> <namespace> <slug> <version> <artifact-folder> -c cfg.json`