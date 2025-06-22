# Text constants module

"""
Text constants for memfaceswap project.
All comments are in English. Follows PEP 8 and Google-style docstrings.
"""

"""
Text templates for memfaceswap bot.
All comments are in English. Follows PEP 8 and Google-style docstrings.
"""

GACHIMUCHI_GREETING: str = (
    "🏋️‍♂️ Привет, брат! Добро пожаловать в гачимучи-генератор мемов!\n"
    "Здесь ты можешь сделать стикер с легендарными лицами. Первый стикер бесплатно, потом — только для настоящих мужчин!\n"
    "Готов ворваться в мир настоящих мемов? Пиши /memes и выбирай мем! 💪"
)
NO_MEMES: str = (
    "Братишка, мемов пока нет! Закинь их в папку memes и возвращайся 💪"
)
MEME_CAPTION = lambda idx, meme_file: f"Мем #{idx}: {meme_file} — только для элиты!"
MEME_CHOOSE_BTN: str = "Выбрать"
MEME_SELECTED = (
    lambda meme_file: f"Мем выбран: {meme_file}! Теперь кидай своё фото для свапа, чемпион 💪"
)
PHOTO_OUT_OF_TURN: str = "Сначала выбери мем через /memes, брат 💪"
PHOTO_RECEIVED = (
    lambda meme_file: f"Фото получено! Мем: {meme_file}\nГотовлю магию гачи! 🪄"
)
UPLOAD_TO_SERVER: str = "Загружаю мем и твоё фото на сервер... 🏋️‍♂️"
FACE_DETECTION: str = "Запускаю поиск лиц... Готовься стать легендой! 🪄"
NO_FACE_FOUND: str = (
    "Не удалось найти лицо на одной из фоток, брат! Попробуй другое фото."
)
FACE_SWAP_PROCESS: str = "Запускаю процесс свапа лиц... 💪"
WAIT_PROCESS: str = "Жду завершения обработки... ⏳"
STICKERSET_CREATED = (
    lambda name: f"Твой стикерпак создан: https://t.me/addstickers/{name} — теперь ты в гачи-элите!"
)
STICKER_ADDED = (
    lambda name: f"New sticker added to your pack!\nYour pack: https://t.me/addstickers/{name}"
)
STICKERSET_ALREADY = (
    lambda name: f"Pack was already created earlier, added sticker to it!\nYour pack: https://t.me/addstickers/{name}"
)
STICKERSET_BROKEN: str = (
    "Looks like the pack was deleted or broken. Try again — a new pack will be created."
)
STICKERSET_CREATE_ERR = lambda e: f"Sticker set creation error: {e}"
STICKER_ADD_ERR = lambda e: f"Sticker add error: {e}"
STICKER_CREATE_FAIL: str = "Could not create sticker, here is just an image!"
FACE_SWAP_FAIL: str = (
    "Something went wrong with face swap, bro! Try again or type /memes."
)
PHOTO_SAVE_FAIL: str = (
    "Something went wrong saving the photo, bro! Try again or type /memes."
)
