"""
Централизованный роутер для memfaceswap.
Стиль RecallDev, только import module, type hints, docstring на русском.
"""

import src.bot.views.handle_photo as handle_photo_view
import src.bot.views.meme_select as meme_select_view
import src.bot.views.memes as memes_view
import src.bot.views.start as start_view
import telegram_rest_mvc.router as mvc_router

router = mvc_router.Router()

mvc_router.path(router, "/start", start_view.StartView, name="start")
mvc_router.path(router, "/memes", memes_view.MemesView, name="memes")
mvc_router.callback(
    router, r"^select_meme:(.+)$", meme_select_view.MemeSelectView, name="select_meme"
)
mvc_router.photo(router, handle_photo_view.HandlePhotoView, name="handle_photo")
