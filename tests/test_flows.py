import pytest
from unittest.mock import MagicMock, patch, mock_open, AsyncMock
import src.bot.flows.face_swap_flow as flow
import src.constants.texts as texts

class DummyFile:
    async def download_as_bytearray(self):
        return b"fakeimg"

class DummyBot:
    def __init__(self):
        self.get_file = AsyncMock(return_value=DummyFile())

class DummyContext:
    def __init__(self):
        self.bot = DummyBot()

class DummyPhoto:
    def __init__(self, file_id="photo_id"):
        self.file_id = file_id

class DummyMessage:
    def __init__(self, photo=None):
        self.photo = photo or [DummyPhoto()]

class DummyUpdate:
    def __init__(self, photo=None):
        self.message = DummyMessage(photo)

class TestFaceSwapFlow:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_state, meme_file, meme_faces, user_faces, job_id, result_url, result_exception, expected_status, expected_error", [
        (None, None, None, None, None, None, None, "error", texts.PHOTO_OUT_OF_TURN),
        (type('DummyUserState', (), {'meme': "test_meme.jpg"})(), "test_meme.jpg", [], ["face"], "jobid", "url", None, "error", texts.NO_FACE_FOUND),
        (type('DummyUserState', (), {'meme': "test_meme.jpg"})(), "test_meme.jpg", ["face"], [], "jobid", "url", None, "error", texts.NO_FACE_FOUND),
        (type('DummyUserState', (), {'meme': "test_meme.jpg"})(), "test_meme.jpg", ["face"], ["face"], "jobid", None, None, "error", "FACE_SWAP_TIMEOUT"),
        (type('DummyUserState', (), {'meme': "test_meme.jpg"})(), "test_meme.jpg", ["face"], ["face"], "jobid", "url", Exception("fail"), "error", "fail"),
    ])
    async def test_face_swap_flow_errors(self, user_state, meme_file, meme_faces, user_faces, job_id, result_url, result_exception, expected_status, expected_error, monkeypatch):
        update = DummyUpdate()
        context = DummyContext()
        user_id = 42
        imgbb_api_key = "imgbb"
        maxstudio_api_key = "maxstudio"
        class DummySession:
            def __enter__(self): return MagicMock()
            def __exit__(self, exc_type, exc_val, exc_tb): pass
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.get_session", lambda: DummySession())
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.get_user_state", lambda session, user_id: user_state)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.upload_to_imgbb", lambda f, k: "http://imgbb.com/img.jpg")
        def detect_face_side_effect(url, key):
            if not hasattr(detect_face_side_effect, "calls"): detect_face_side_effect.calls = 0
            detect_face_side_effect.calls += 1
            return meme_faces if detect_face_side_effect.calls == 1 else user_faces
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.detect_face", detect_face_side_effect)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.swap_face", lambda url, faces, key: job_id)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.poll_job_status", lambda job_id, key: result_url)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.clear_user_state", lambda session, user_id: None)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.image.convert_to_sticker_image", lambda content, path: None)
        if result_exception:
            with patch("builtins.open", mock_open(read_data=b"fakeimg")):
                with patch("requests.get", side_effect=result_exception):
                    result = await flow.face_swap_flow(update, context, user_id, imgbb_api_key, maxstudio_api_key)
        else:
            class DummyResp:
                content = b"fakewebp"
                def raise_for_status(self): pass
            with patch("builtins.open", mock_open(read_data=b"fakeimg")):
                with patch("requests.get", return_value=DummyResp()):
                    result = await flow.face_swap_flow(update, context, user_id, imgbb_api_key, maxstudio_api_key)
        assert result["status"] == expected_status

    @pytest.mark.asyncio
    async def test_face_swap_flow_exception(self, monkeypatch):
        update = DummyUpdate()
        context = DummyContext()
        user_id = 42
        imgbb_api_key = "imgbb"
        maxstudio_api_key = "maxstudio"
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.get_session", lambda: MagicMock())
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.get_user_state", lambda session, user_id: type('DummyUserState', (), {'meme': "test_meme.jpg"})())
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.upload_to_imgbb", lambda f, k: "http://imgbb.com/img.jpg")
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.detect_face", lambda url, key: ["face"])
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.swap_face", lambda url, faces, key: "jobid")
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.poll_job_status", lambda jobid, key: "url")
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.clear_user_state", lambda session, user_id: None)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.image.convert_to_sticker_image", lambda content, path: None)
        with patch("builtins.open", mock_open(read_data=b"fakeimg")):
            with patch("requests.get", side_effect=Exception("fail")):
                result = await flow.face_swap_flow(update, context, user_id, imgbb_api_key, maxstudio_api_key)
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_face_swap_flow_success(self, monkeypatch):
        update = DummyUpdate()
        context = DummyContext()
        user_id = 42
        imgbb_api_key = "imgbb"
        maxstudio_api_key = "maxstudio"
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.get_session", lambda: MagicMock())
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.get_user_state", lambda session, user_id: type('DummyUserState', (), {'meme': "test_meme.jpg"})())
        monkeypatch.setattr("src.bot.flows.face_swap_flow.face_api.upload_to_imgbb", lambda f, k: "http://imgbb.com/img.jpg")
        # Мокаем face_api
        monkeypatch.setattr("src.services.face_api.detect_face", lambda url, key: ["face"])
        monkeypatch.setattr("src.services.face_api.swap_face", lambda url, faces, key: "jobid")
        monkeypatch.setattr("src.services.face_api.poll_job_status", lambda jobid, key: "http://result.url/sticker.webp")
        monkeypatch.setattr("src.bot.flows.face_swap_flow.db_services.clear_user_state", lambda session, user_id: None)
        monkeypatch.setattr("src.bot.flows.face_swap_flow.image.convert_to_sticker_image", lambda content, path: None)
        with patch("os.makedirs") as _makedirs:
            with patch("builtins.open", mock_open(read_data=b"fakeimg")):
                class DummyResp:
                    content = b"fakewebp"
                    def raise_for_status(self): pass
                with patch("requests.get", return_value=DummyResp()):
                    result = await flow.face_swap_flow(update, context, user_id, imgbb_api_key, maxstudio_api_key)
        print("RESULT_DEBUG:", result)
        assert result["status"] == "ok"
        assert "sticker_path" in result
        assert result["text"].startswith("Твой стикерпак создан")
