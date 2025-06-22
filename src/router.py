"""
Декларация маршрутов для memfaceswap.
"""

from src.views.handle_photo import HandlePhotoView
from src.views.meme_select import MemeSelectView
from src.views.memes import MemesView
from src.views.start import StartView
from telegram_rest_mvc.router import Router, callback, path, photo

router = Router()

path(router, "/start", StartView.as_handler(), name="start")
path(router, "/memes", MemesView.as_handler(), name="memes")
callback(router, r"^select_meme:(.+)$", MemeSelectView.as_handler(), name="select_meme")
photo(router, HandlePhotoView.as_handler(), name="handle_photo")
