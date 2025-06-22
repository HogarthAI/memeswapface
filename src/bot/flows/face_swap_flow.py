"""
Face swap flow: process user photo, run face swap, create sticker.
Returns dict with result for View. Does not use Telegram API directly.
Follows RecallDev, SOLID, PEP 8, Google-style docstrings, flat code.
"""

import os
from typing import Any, Dict
from uuid import uuid4

import src.constants.constants as constants
import src.constants.texts as texts
import src.db.services as db_services
import src.services.face_api as face_api
import src.services.image as image
import src.utils as utils


async def face_swap_flow(
    update: Any,
    context: Any,
    user_id: int,
    imgbb_api_key: str,
    maxstudio_api_key: str,
) -> Dict[str, Any]:
    """
    Business logic pipeline for face swap: photo upload, upload_to_imgbb, detect_face, swap_face, poll_job_status, sticker creation, user state cleanup.
    Does not call Telegram API directly.

    Args:
        update (Any): Telegram update.
        context (Any): Telegram context.
        user_id (int): User ID.
        imgbb_api_key (str): imgbb API key.
        maxstudio_api_key (str): maxstudio API key.

    Returns:
        dict: Result of the flow.
    """
    stage_msgs = []
    try:
        with db_services.get_session() as session:
            user_state = db_services.get_user_state(session, user_id)
            meme_file = user_state.meme if user_state else None
        if not meme_file:
            return {"status": "error", "error": texts.PHOTO_OUT_OF_TURN}

        # Download user photo
        photo = update.message.photo[-1]
        photo_file = await context.bot.get_file(photo.file_id)
        photo_bytes = await photo_file.download_as_bytearray()
        user_photo_path = f"photos/user_{user_id}_{uuid4().hex}.jpg"
        os.makedirs(os.path.dirname(user_photo_path), exist_ok=True)
        with open(user_photo_path, "wb") as f:
            f.write(photo_bytes)

        # Upload meme and user photo to imgbb
        meme_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "..",
            "memes",
            meme_file,
        )
        from io import BytesIO
        with open(meme_path, "rb") as f:
            meme_bytes = BytesIO(f.read())
        meme_url = face_api.upload_to_imgbb(meme_bytes, imgbb_api_key)

        with open(user_photo_path, "rb") as f:
            user_bytes = BytesIO(f.read())
        user_url = face_api.upload_to_imgbb(user_bytes, imgbb_api_key)

        # Промежуточные сообщения для View
        stage_msgs = []
        stage_msgs.append("Делаю магию face detection... 🪄")
        meme_faces = face_api.detect_face(meme_url, maxstudio_api_key)
        user_faces = face_api.detect_face(user_url, maxstudio_api_key)
        if not meme_faces or not user_faces:
            return {"status": "error", "error": texts.NO_FACE_FOUND, "stage_msgs": stage_msgs}

        # Prepare face swap data
        face_swap_faces = [{"originalFace": meme_faces[0], "newFace": user_url}]
        stage_msgs.append("Запускаю процесс face swap... 💪")
        job_id = face_api.swap_face(meme_url, face_swap_faces, maxstudio_api_key)
        stage_msgs.append("Ожидаю завершения обработки... ⏳")
        result_url = face_api.poll_job_status(job_id, maxstudio_api_key)
        if not result_url:
            return {"status": "error", "error": texts.FACE_SWAP_TIMEOUT, "stage_msgs": stage_msgs}

        # Download result and create sticker
        import requests

        resp = requests.get(result_url)
        resp.raise_for_status()
        sticker_path = f"photos/sticker_{user_id}_{uuid4().hex}.webp"
        image.convert_to_sticker_image(resp.content, sticker_path)

        # Cleanup user state
        with db_services.get_session() as session:
            db_services.clear_user_state(session, user_id)

        return {
            "status": "ok",
            "sticker_path": sticker_path,
            "text": texts.STICKERSET_CREATED("memfaceswap"),
            "stage_msgs": stage_msgs,
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "stage_msgs": stage_msgs}
