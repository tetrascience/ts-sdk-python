from ts_sdk.taskdev import Context, load_test_file, load_pipeline_config, check_test_output

def test_taskdev_should_load_text_file():
    c = Context({}) 
    f = load_test_file(c, __file__, '/datalake/path', file_category='RAW')
    assert f == {'type': 's3file', 'bucket': 'fake-unittest-bucket', 'fileKey': '/datalake/path'}

def test_taskdev_should_load_bin_file():
    c = Context({}) 
    f = load_test_file(c, '/bin/ls', '/datalake/path', file_category='RAW', mode='rb')
    assert f == {'type': 's3file', 'bucket': 'fake-unittest-bucket', 'fileKey': '/datalake/path'}