"""
Sticker set creation/add logic (Telegram API), copy-paste from working bot.py.
All comments in English. PEP8, Google-style docstrings.
"""
import re
import random
import string
from telegram import InputSticker
from telegram.error import TelegramError

async def create_or_add_sticker_to_set(context, update, user_id, username, bot_username, sticker_path, emojis="💪") -> str:
    """
    Creates or adds a sticker to user's sticker set. Returns URL or error string.
    Args:
        context: Telegram context
        update: Telegram update
        user_id: int
        username: str or None
        bot_username: str
        sticker_path: str (path to .webp sticker)
        emojis: str (default: muscle)
    Returns:
        str: URL to sticker set or error message
    """
    set_title = "Создать gachimuchi мемы -> @gachimuchi_swap_bot"
    set_desc = "Создать гачимучи-стикеры в боте @gachimuchi_swap_bot"
    def safe_name(s):
        return re.sub(r'[^a-zA-Z0-9_]', '_', s or '')
    if username:
        user_tag_val = username
    else:
        user_tag_val = str(user_id)
    user_tag_safe = safe_name(user_tag_val)
    bot_username_safe = safe_name(bot_username)
    max_user_tag_len = 64 - (len('gachi___by_') + len(bot_username_safe))
    user_tag_safe = user_tag_safe[:max_user_tag_len]
    sticker_set_name = f"gachi_{user_tag_safe}_by_{bot_username_safe}".lower()
    try:
        with open(sticker_path, "rb") as sticker_file:
            sticker = InputSticker(sticker=sticker_file, emoji_list=[emojis], format="static")
            try:
                await context.bot.create_new_sticker_set(
                    user_id=user_id,
                    name=sticker_set_name,
                    title=set_title + " | " + set_desc,
                    stickers=[sticker],
                    sticker_type="regular"
                )
                return f"https://t.me/addstickers/{sticker_set_name}"
            except TelegramError as e:
                if "is already occupied" in str(e):
                    try:
                        await context.bot.add_sticker_to_set(
                            user_id=user_id,
                            name=sticker_set_name,
                            sticker=sticker
                        )
                        return f"https://t.me/addstickers/{sticker_set_name}"
                    except TelegramError as e2:
                        return f"Пак был удалён или повреждён. Попробуй ещё раз: {e2}"
                else:
                    return f"Ошибка создания стикерсета: {e}"
    except Exception as e:
        return f"Ошибка при создании стикера: {e}"
