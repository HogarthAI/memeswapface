import pytest
from unittest.mock import patch, MagicMock
import src.services.face_api as face_api
import src.services.image as image
from PIL import Image
import io
import os
import src.db.models as models
import src.db.services as user_state
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class TestFaceApi:
    def test_swap_face_file_success(self, tmp_path):
        dummy_photo = tmp_path / "photo.jpg"
        dummy_photo.write_bytes(b"fakeimg")
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {"result": {"mediaUrl": "https://result.url/img.webp"}}
            mock_post.return_value = mock_resp
            url = face_api.swap_face_file("https://meme.url/meme.png", str(dummy_photo), "APIKEY")
            assert url == "https://result.url/img.webp"

    def test_swap_face_file_fail(self, tmp_path):
        dummy_photo = tmp_path / "photo.jpg"
        dummy_photo.write_bytes(b"fakeimg")
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("fail")
            mock_post.return_value = mock_resp
            with pytest.raises(Exception):
                face_api.swap_face_file("https://meme.url/meme.png", str(dummy_photo), "APIKEY")

    def test_poll_job_status_success(self):
        with patch("src.services.face_api.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 200
            mock_resp.json.return_value = {"status": "completed", "result": {"mediaUrl": "https://result.url/img.webp"}}
            mock_get.return_value = mock_resp
            url = face_api.poll_job_status("jobid", "APIKEY", timeout=1)
            assert url == "https://result.url/img.webp"

    def test_poll_job_status_timeout(self):
        with patch("src.services.face_api.requests.get") as mock_get:
            mock_resp = MagicMock()
            mock_resp.status_code = 404
            mock_get.return_value = mock_resp
            with pytest.raises(TimeoutError):
                face_api.poll_job_status("jobid", "APIKEY", timeout=2)

    def test_upload_to_imgbb_success(self):
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {"data": {"url": "http://imgbb.com/fake.png"}}
            mock_post.return_value = mock_resp
            result = face_api.upload_to_imgbb(MagicMock(getvalue=lambda: b"img"), "APIKEY")
            assert result == "http://imgbb.com/fake.png"

    def test_upload_to_imgbb_fail(self):
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("fail")
            mock_post.return_value = mock_resp
            with pytest.raises(Exception):
                face_api.upload_to_imgbb(MagicMock(getvalue=lambda: b"img"), "APIKEY")

    def test_detect_face_success(self):
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {"detectedFaces": ["face1"]}
            mock_post.return_value = mock_resp
            result = face_api.detect_face("http://img.url", "APIKEY")
            assert result == ["face1"]

    def test_detect_face_fail(self):
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.side_effect = Exception("fail")
            mock_post.return_value = mock_resp
            with pytest.raises(Exception):
                face_api.detect_face("http://img.url", "APIKEY")

    def test_swap_face_success(self, tmp_path):
        dummy_photo = tmp_path / "photo.jpg"
        dummy_photo.write_bytes(b"fakeimg")
        with patch("src.services.face_api.requests.post") as mock_post:
            mock_resp = MagicMock()
            mock_resp.raise_for_status.return_value = None
            mock_resp.json.return_value = {"jobId": "test_job_id"}
            mock_post.return_value = mock_resp
            job_id = face_api.swap_face("https://meme.url/meme.png", {"face": "data"}, "APIKEY")
            assert job_id == "test_job_id"

class TestImageService:
    def test_convert_to_sticker_image_success(self, tmp_path):
        img = Image.new("RGBA", (300, 600), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        out_path = tmp_path / "out.webp"
        result = image.convert_to_sticker_image(buf.getvalue(), str(out_path))
        assert os.path.exists(result)
        out_img = Image.open(result)
        assert out_img.size == (512, 512)
        assert out_img.mode in ("RGB", "RGBA")

    def test_convert_to_sticker_image_invalid_bytes(self, tmp_path):
        out_path = tmp_path / "fail.webp"
        with pytest.raises(Exception):
            image.convert_to_sticker_image(b"notanimage", str(out_path))

    def test_convert_to_sticker_image_empty_bytes(self, tmp_path):
        out_path = tmp_path / "empty.webp"
        with pytest.raises(Exception):
            image.convert_to_sticker_image(b"", str(out_path))

    def test_convert_to_sticker_image_alt(self, tmp_path):
        img = Image.new("RGBA", (300, 600), (255, 0, 0, 255))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        out_path = tmp_path / "out2.webp"
        image.convert_to_sticker_image(buf.getvalue(), str(out_path))
        out_img = Image.open(out_path)
        assert out_img.size == (512, 512)
        assert out_img.mode in ("RGB", "RGBA")

class TestUserStateService:
    DATABASE_URL = "sqlite:///:memory:"
    @pytest.fixture(scope="function")
    def sync_session(self):
        engine = create_engine(self.DATABASE_URL, echo=False)
        models.Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
        engine.dispose()

    def test_user_state_crud(self, sync_session):
        user_state.set_user_state(sync_session, 42, meme="meme42", sticker_set_name="set42")
        user = user_state.get_user_state(sync_session, 42)
        assert user is not None
        assert user.sticker_set_name == "set42"
        assert user.meme == "meme42"
        user_state.set_user_state(sync_session, 42, meme="meme43")
        user = user_state.get_user_state(sync_session, 42)
        assert user.meme == "meme43"
        user_state.clear_user_state(sync_session, 42)
        user = user_state.get_user_state(sync_session, 42)
        assert user is None
