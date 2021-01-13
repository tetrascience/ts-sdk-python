# ts-sdk
Tetrascience Python SDK for task scripts build and test

## Unit tests

```
from ts_sdk.taskdev import Context, load_test_input, load_pipeline_config, check_test_output

ctx = Context()
load_pipeline_config(ctx, ...)
input = load_test_input(ctx, ...)
task_script_fn(input, ctx)
check_test_output(ctx, ...)
```

WIP...

## Dockerfile ENTRYPOINT

```
ENTRYPOINT [ "<python-bin>", "-u", "-m", "ts_sdk.task.run_reuse_loop" ]
```
