from ts_sdk import task

def test_log(input, context: task.Context):
    logger = context.get_logger()
    logger.log({
        "message": "Hello from test function!",
        "level": "info"
    })

def test_file_operations(input, context: task.Context):
    file = context.write_file(b'test-content', 'write_file_name', 'PROCESSED')  
    file = context.add_attributes(file, {'k1': 'v1'}, ['t1'], [{'name': 'label_name', 'value': 'label_value'}])
    result = context.read_file(file)
    assert result['body'] == b'test-content', 'read_file content differs from provided in write_file'


def test_all(input, context: task.Context):
    test_log(input, context)
    test_file_operations(input, context)
    return True
