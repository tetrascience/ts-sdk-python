def test_fn(input, context):
    logger = context.get_logger()

    logger.log({
        "message": "Hello from test function!",
        "level": "info"
    })