import sys
from unittest.mock import patch
from ts_sdk.task.run_reuse_loop import task_process_fn

task = {
    'context': {},
    'func_dir': '.',
    'func': 'slug'
}

def __sys_exit_side_effect(*args, **kwargs):
    sys.exit('Test exit')

@patch('ts_sdk.task.run_reuse_loop.run')
def test_task_process_fn_should_return_result(patched_run):
    shared_dict = {'result': None, 'error': None}
    patched_run.return_value = 'ok'
    task_process_fn(task, shared_dict)
    assert shared_dict['error'] == None
    assert shared_dict['result'] == 'ok'

@patch('ts_sdk.task.run_reuse_loop.run')
def test_task_process_fn_should_return_error(patched_run):
    shared_dict = {'result': None, 'error': None}
    patched_run.side_effect = Exception('Boom!')
    task_process_fn(task, shared_dict)
    assert shared_dict['result'] == None
    assert 'Traceback' in shared_dict['error']

@patch('ts_sdk.task.run_reuse_loop.run')
def test_task_process_fn_should_handle_sysexit(patched_run):
    shared_dict = {'result': None, 'error': None}
    patched_run.side_effect = __sys_exit_side_effect
    task_process_fn(task, shared_dict)
    assert shared_dict['result'] == None
    assert 'Traceback' in shared_dict['error']