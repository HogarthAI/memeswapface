import pytest
from unittest.mock import patch, mock_open, MagicMock
import src.views.handle_photo as handle_photo
import src.views.meme_select as meme_select
import src.views.memes as memes
import src.constants.texts as texts
from src.constants import constants
from tests.conftest import DummyUpdate, DummyContext, DummyMessage
import src.bot.flows.sticker_set_flow as sticker_set_flow
from telegram.error import TelegramError
import builtins
import pytest
from unittest.mock import patch, mock_open, MagicMock, AsyncMock

@pytest.mark.asyncio
async def test_create_sticker_set_success(monkeypatch, tmp_path):
    context = MagicMock()
    update = MagicMock()
    context.bot.create_new_sticker_set = AsyncMock(return_value=True)
    context.bot.add_sticker_to_set = AsyncMock()
    bot_username = "bot"
    username = "user"
    sticker_path = tmp_path / "sticker.webp"
    sticker_path.write_bytes(b"fakewebp")
    with patch("builtins.open", mock_open(read_data=b"fakewebp")):
        with patch("src.bot.flows.sticker_set_flow.InputSticker", return_value=MagicMock()):
            url = await sticker_set_flow.create_or_add_sticker_to_set(context, update, 1, username, bot_username, str(sticker_path))
            assert "https://t.me/addstickers/" in url

@pytest.mark.asyncio
async def test_create_sticker_set_already_exists_success(monkeypatch, tmp_path):
    context = MagicMock()
    update = MagicMock()
    context.bot.create_new_sticker_set = AsyncMock(side_effect=TelegramError("is already occupied"))
    context.bot.add_sticker_to_set = AsyncMock(return_value=True)
    bot_username = "bot"
    username = "user"
    sticker_path = tmp_path / "sticker.webp"
    sticker_path.write_bytes(b"fakewebp")
    with patch("builtins.open", mock_open(read_data=b"fakewebp")):
        with patch("src.bot.flows.sticker_set_flow.InputSticker", return_value=MagicMock()):
            url = await sticker_set_flow.create_or_add_sticker_to_set(context, update, 1, username, bot_username, str(sticker_path))
            assert "https://t.me/addstickers/" in url

@pytest.mark.asyncio
async def test_create_sticker_set_already_exists_fail(monkeypatch, tmp_path):
    context = MagicMock()
    update = MagicMock()
    context.bot.create_new_sticker_set = AsyncMock(side_effect=TelegramError("is already occupied"))
    context.bot.add_sticker_to_set = AsyncMock(side_effect=TelegramError("fail add"))
    bot_username = "bot"
    username = "user"
    sticker_path = tmp_path / "sticker.webp"
    sticker_path.write_bytes(b"fakewebp")
    with patch("builtins.open", mock_open(read_data=b"fakewebp")):
        with patch("src.bot.flows.sticker_set_flow.InputSticker", return_value=MagicMock()):
            msg = await sticker_set_flow.create_or_add_sticker_to_set(context, update, 1, username, bot_username, str(sticker_path))
            assert "Пак был удалён" in msg

@pytest.mark.asyncio
async def test_create_sticker_set_fail(monkeypatch, tmp_path):
    context = MagicMock()
    update = MagicMock()
    context.bot.create_new_sticker_set = AsyncMock(side_effect=TelegramError("fail generic"))
    context.bot.add_sticker_to_set = AsyncMock()
    bot_username = "bot"
    username = "user"
    sticker_path = tmp_path / "sticker.webp"
    sticker_path.write_bytes(b"fakewebp")
    with patch("builtins.open", mock_open(read_data=b"fakewebp")):
        with patch("src.bot.flows.sticker_set_flow.InputSticker", return_value=MagicMock()):
            msg = await sticker_set_flow.create_or_add_sticker_to_set(context, update, 1, username, bot_username, str(sticker_path))
            assert "Ошибка создания стикерсета" in msg

@pytest.mark.asyncio
async def test_create_sticker_file_not_found(monkeypatch, tmp_path):
    context = MagicMock()
    update = MagicMock()
    context.bot.create_new_sticker_set = AsyncMock()
    context.bot.add_sticker_to_set = AsyncMock()
    bot_username = "bot"
    username = "user"
    sticker_path = tmp_path / "nofile.webp"
    with patch("builtins.open", side_effect=FileNotFoundError("not found")):
        msg = await sticker_set_flow.create_or_add_sticker_to_set(context, update, 1, username, bot_username, str(sticker_path))
        assert "Ошибка при создании стикера" in msg

@pytest.mark.asyncio
async def test_create_sticker_unexpected_exception(monkeypatch, tmp_path):
    context = MagicMock()
    update = MagicMock()
    context.bot.create_new_sticker_set = AsyncMock()
    context.bot.add_sticker_to_set = AsyncMock()
    bot_username = "bot"
    username = "user"
    sticker_path = tmp_path / "sticker.webp"
    sticker_path.write_bytes(b"fakewebp")
    with patch("builtins.open", mock_open(read_data=b"fakewebp")):
        with patch("src.bot.flows.sticker_set_flow.InputSticker", side_effect=Exception("fail sticker")):
            msg = await sticker_set_flow.create_or_add_sticker_to_set(context, update, 1, username, bot_username, str(sticker_path))
            assert "Ошибка при создании стикера" in msg

class TestHandlePhotoView:
    @pytest.mark.asyncio
    async def test_success(self, monkeypatch):
        update = DummyUpdate()
        update.message = DummyMessage()
        context = DummyContext(message=update.message)
        async def async_flow(**kwargs):
            print("ASYNC_FLOW_CALLED")
            return {
                "status": "ok",
                "sticker_path": "path/to/sticker.webp",
                "text": "Твой стикерпак создан: https://t.me/addstickers/test_pack — теперь ты в гачи-элите!",
                "stage_msgs": [],
            }
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_swap_flow", async_flow)
        async def dummy_create_or_add_sticker_to_set(*a, **kw):
            return "https://t.me/addstickers/test_pack"
        monkeypatch.setattr(
            "src.bot.flows.sticker_set_flow.create_or_add_sticker_to_set",
            dummy_create_or_add_sticker_to_set,
        )
        view = handle_photo.HandlePhotoView(update, context)
        view.update = update
        view.context = context
        await view.command()
        replies = update.message.replies
        print("DEBUG", replies)
        assert any("sticker" in r[0] and r[1] == "path/to/sticker.webp" for r in replies)
        assert any("text" in r[0] and "стикерпак" in r[1] for r in replies) 

    @pytest.mark.asyncio
    async def test_file_not_found(self, monkeypatch):
        update = DummyUpdate()
        update.message = DummyMessage()
        context = DummyContext(message=update.message)
        async def async_flow(**kwargs):
            return {"status": "error", "error": "file not found"}
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_swap_flow", async_flow)
        view = handle_photo.HandlePhotoView(update, context)
        view.update = update
        view.context = context
        await view.command()
        replies = update.message.replies
        assert any("text" in r[0] and ("not found" in r[1].lower() or "нет файла" in r[1].lower()) for r in replies)

    @pytest.mark.asyncio
    async def test_exception(self, monkeypatch):
        update = DummyUpdate()
        update.message = DummyMessage()
        context = DummyContext(message=update.message)
        async def async_flow(**kwargs):
            raise Exception("fail")
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_swap_flow", async_flow)
        view = handle_photo.HandlePhotoView(update, context)
        view.update = update
        view.context = context
        await view.command()
        replies = update.message.replies
        assert any("text" in r[0] and texts.FACE_SWAP_FAIL in r[1] for r in replies)

    @pytest.mark.asyncio
    async def test_swap_error(self, monkeypatch):
        update = DummyUpdate()
        update.message = DummyMessage()
        context = DummyContext(message=update.message)
        async def async_flow(**kwargs):
            return {"status": "error", "error": "ошибка"}
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_swap_flow", async_flow)
        view = handle_photo.HandlePhotoView(update, context)
        view.update = update
        view.context = context
        await view.command()
        replies = update.message.replies
        assert any("text" in r[0] and ("ошибка" in r[1].lower() or "error" in r[1].lower()) for r in replies)

class TestMemeSelectView:
    @pytest.mark.asyncio
    async def test_callback_correct_usage(self, monkeypatch):
        update = MagicMock()
        context = MagicMock()
        update.effective_user.id = 123
        update.message = MagicMock()
        meme_file = "test_meme.webp"
        monkeypatch.setattr(meme_select, "db_services", MagicMock())
        monkeypatch.setattr(meme_select, "user_state", MagicMock())
        monkeypatch.setattr(meme_select.utils, "get_effective_message", lambda u, c: update.message)
        called = {}
        def fake_reply_text(text):
            called["text"] = text
        update.message.reply_text.side_effect = fake_reply_text
        view = meme_select.MemeSelectView(update, context)
        view.update = update
        view.context = context
        # Не должно быть AttributeError
        try:
            await view.callback(meme_file)
        except AttributeError as e:
            pytest.fail(f"AttributeError: {e}")
        assert called["text"] == texts.MEME_SELECTED(meme_file)

class TestMemesView:
    @pytest.mark.asyncio
    async def test_memes_command_success(self, monkeypatch):
        update = DummyUpdate()
        context = DummyContext(message=update.message)
        monkeypatch.setattr("os.listdir", lambda path: ["meme1.png"])
        monkeypatch.setattr("builtins.open", mock_open(read_data=b"fakeimg"))
        view = memes.MemesView(update, context)
        view.update = update
        view.context = context
        await view.command()
        assert any("Мем #1: meme1 — только для элиты!" in reply[1] for reply in update.message.replies)

    @pytest.mark.asyncio
    async def test_memes_command_no_files(self, monkeypatch):
        update = DummyUpdate()
        context = DummyContext(message=update.message)
        monkeypatch.setattr("os.listdir", lambda path: [])
        view = memes.MemesView(update, context)
        view.update = update
        view.context = context
        await view.command()
        assert any(constants.NO_MEMES.lower() in reply[1].lower() for reply in update.message.replies)
