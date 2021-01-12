# ts-sdk-python
A public repo for Tetrascience task script Python SDK

## Local pipeline execution

WIP...

## Unit tests

```
from ts_sdk.taskdev import Context, load_test_input, load_pipeline_config, check_test_output

ctx = Context()
load_pipeline_config(ctx, ...)
load_pipeline_config(ctx, ...)
task_script_fn(input, ctx)
check_test_output(...)
```

## Dockerfile ENTRYPOINT

```
ENTRYPOINT [ "<python-bin>", "-u", "-m", "ts_sdk.task.run_reuse_loop" ]
```
