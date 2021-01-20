import sys
import os
import datetime
import pytest
from unittest.mock import MagicMock

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "ts_sdk"))
from task.__task_script_runner import Context

class LogMock:
    def log(self, data):
        print(data)

class DatalakeMock:
    def read_file(self, file, form):
        return {}

idsMock = { 
    'get_ids': lambda **args: print(args), 
    'validate_ids': lambda **args: print(args)
    }

class CommandMock:
    def x(self, **args):
        print(args)

def test_context_test_misc():
    log = LogMock()
    command = CommandMock()

    Context.log = log
    c = Context(
        {}, 
        DatalakeMock(), 
        idsMock, 
        log, 
        CommandMock())
    
    r = c.read_file({})
    assert r == {}
