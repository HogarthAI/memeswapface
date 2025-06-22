"""
External face API related services.
All comments must be in English. Follows PEP 8 and Google-style docstrings.
"""

from typing import Any, Dict, Optional

import requests


def detect_face(image_url: str, api_key: str) -> Any:
    """
    Detects faces in an image using the maxstudio API (как в bot.py).
    """
    url = "https://api.maxstudio.ai/detect-face-image"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"imageUrl": image_url})
    resp.raise_for_status()
    return resp.json().get("detectedFaces", [])


def swap_face(media_url: str, faces: Any, api_key: str) -> str:
    """
    Starts the face swap process using the maxstudio API (как в bot.py).
    """
    url = "https://api.maxstudio.ai/swap-image"
    headers = {"x-api-key": api_key, "Content-Type": "application/json"}
    resp = requests.post(url, headers=headers, json={"mediaUrl": media_url, "faces": faces})
    resp.raise_for_status()
    return resp.json()["jobId"]


def swap_face_file(media_url: str, user_photo_path: str, api_key: str) -> str:
    """
    Calls the maxstudio face swap API with a file and returns the result mediaUrl (структура как в bot.py, если потребуется).
    """
    url = "https://api.maxstudio.ai/swap-image"
    with open(user_photo_path, "rb") as f:
        files = {"file": f}
        data = {"template": media_url}
        headers = {"x-api-key": api_key}
        resp = requests.post(url, files=files, data=data, headers=headers)
        resp.raise_for_status()
        result = resp.json()
        return result["result"]["mediaUrl"]


def upload_to_imgbb(image: "BytesIO", api_key: str) -> str:
    """
    Uploads an image to imgbb and returns the image URL.
    ...
    """
    response = requests.post(
        "https://api.imgbb.com/1/upload",
        params={"key": api_key},
        files={"image": image.getvalue()},
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()
    return data["data"]["url"]


def poll_job_status(job_id: str, api_key: str, timeout: int = 60) -> Optional[str]:
    """
    Polls the status of a face swap job and returns the result mediaUrl if completed (как в bot.py).
    """
    import time
    url = f"https://api.maxstudio.ai/swap-image/{job_id}"
    headers = {"x-api-key": api_key}
    for _ in range(timeout):
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        if data.get("status") == "completed":
            return data["result"]["mediaUrl"]
        elif data.get("status") == "failed":
            raise Exception("Face swap failed")
        time.sleep(2)
    raise TimeoutError("Face swap job timed out")
