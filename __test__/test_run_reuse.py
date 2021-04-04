import sys
from unittest.mock import patch
from ts_sdk.task.run_reuse_loop import task_process_fn, last_run

task = {
    'context': {},
    'func_dir': '.',
    'func': 'slug'
}

def __sys_exit_side_effect(*args, **kwargs):
    sys.exit('Test exit')

@patch('ts_sdk.task.run_reuse_loop.run')
def test_task_process_fn_should_return_result(patched_run):
    last_run['result'] = None
    last_run['error'] = None
    patched_run.return_value = 'ok'
    task_process_fn(task, last_run)
    assert last_run['error'] == None
    assert last_run['result'] == 'ok'

@patch('ts_sdk.task.run_reuse_loop.run')
def test_task_process_fn_should_return_error(patched_run):
    last_run['result'] = None
    last_run['error'] = None
    patched_run.side_effect = Exception('Boom!')
    task_process_fn(task, last_run)
    assert last_run['result'] == None
    assert 'Traceback' in last_run['error']

@patch('ts_sdk.task.run_reuse_loop.run')
def test_task_process_fn_should_handle_sysexit(patched_run):
    last_run['result'] = None
    last_run['error'] = None
    patched_run.side_effect = __sys_exit_side_effect
    task_process_fn(task, last_run)
    assert last_run['result'] == None
    assert 'Traceback' in last_run['error']