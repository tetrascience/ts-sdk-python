from ts_sdk import task

def test_fn(input, context: task.Context):
    logger = context.get_logger()

    logger.log({
        "message": "Hello from test function!",
        "level": "info"
    })

    context.write_file('content', 'write_file_name', 'PROCESSED')