# ts-sdk
Tetrascience Python SDK

## Install

```
pip3 install ts-sdk --dev
```

## Usage

### Init a new protocol

```
ts-tool init -o <org> -m <master-script-slugl> -t <task-script-slug> -f <folder>
```

### Upload artifact

```
ts-tool put <ids|master-script|task-script> <namespace> <slug> <version> <folder>
```

## Dockerfile ENTRYPOINT

```
ENTRYPOINT [ "<python-bin>", "-u", "-m", "ts_sdk.task.run" ]
```
