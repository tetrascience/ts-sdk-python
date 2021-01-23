# ts-sdk
Tetrascience Python SDK

## Install

```
pipenv install ts-sdk --dev
```

## Usage

### Init a new protocol

```
pipenv run ts-tool init -o <org> -m <master-script-slugl> -t <task-script-slug> -f <folder>
```

### Upload artifact

```
pipenv run ts-tool put <ids|c|task-script> <namespace> <slug> <version> <folder>
```

## Dockerfile ENTRYPOINT

```
ENTRYPOINT [ "<python-bin>", "-u", "-m", "ts_sdk.task.run" ]
```
