import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

class DummyPhoto:
    def __init__(self, file_id="photo_id"):
        self.file_id = file_id

class DummyMessage:
    def __init__(self):
        self.replies = []
        self.photo = [DummyPhoto()]
    async def reply_photo(self, photo, caption, reply_markup):
        self.replies.append(('photo', caption, reply_markup))
    async def reply_text(self, text, **kwargs):
        self.replies.append(('text', text))
    async def reply_sticker(self, sticker, **kwargs):
        self.replies.append(('sticker', sticker))

class DummyUpdate:
    def __init__(self):
        self.effective_user = MagicMock(id=123)
        self.message = DummyMessage()

from unittest.mock import AsyncMock, MagicMock

class DummyFile:
    async def download_as_bytearray(self):
        return b"fakeimg"

class DummyContext:
    def __init__(self, message=None):
        self.bot = MagicMock()
        self.bot.get_file = AsyncMock(return_value=DummyFile())
        self.bot.get_me = AsyncMock(return_value=MagicMock(username="test_bot"))
        self.message = message  # ссылка на DummyMessage
        self.bot.send_sticker = message.reply_sticker if message else AsyncMock()
        self.bot.send_message = message.reply_text if message else AsyncMock()
        self.bot.send_photo = message.reply_photo if message else AsyncMock()
