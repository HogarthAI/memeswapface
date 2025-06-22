import pytest
import src.utils as utils

class DummyMessage:
    pass

class DummyUpdate:
    def __init__(self, message=None, edited_message=None, callback_query=None):
        self.message = message
        self.edited_message = edited_message
        self.callback_query = callback_query

class DummyCallbackQuery:
    def __init__(self, message):
        self.message = message

class DummyContext:
    def __init__(self, message=None):
        self.message = message

@pytest.mark.parametrize("update,context,expected", [
    (DummyUpdate(message="msg1"), DummyContext(), "msg1"),
    (DummyUpdate(message=None, edited_message="edit1"), DummyContext(), "edit1"),
    (DummyUpdate(message=None, edited_message=None, callback_query=DummyCallbackQuery("cb1")), DummyContext(), "cb1"),
    (DummyUpdate(message=None, edited_message=None, callback_query=None), DummyContext(message="ctx1"), "ctx1"),
    (DummyUpdate(message=None, edited_message=None, callback_query=None), DummyContext(message=None), None),
])
def test_get_effective_message(update, context, expected):
    assert utils.get_effective_message(update, context) == expected
