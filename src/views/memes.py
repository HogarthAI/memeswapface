"""
View для команды /memes.
Стиль RecallDev: только import module, type hints, docstrings, flat code.
"""

import logging
import os

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

import src.constants.constants as constants
import src.constants.texts as texts
import src.utils as utils
from telegram_rest_mvc import views

logger = logging.getLogger(__name__)


class MemesView(views.View):
    async def command(self):
        """
        Обрабатывает команду /memes: выводит список мемов с кнопками выбора.
        Ведёт подробное логирование этапов.
        """
        logger.info(
            "/memes command started for user_id=%s",
            getattr(self.update.effective_user, "id", None),
        )
        meme_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), "..", "memes"
        )
        try:
            meme_files = [
                f
                for f in os.listdir(meme_dir)
                if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
            ]
        except Exception as e:
            logger.error("Ошибка чтения директории мемов: %s", e)
            await self.update.message.reply_text(constants.NO_MEMES)
            return
        logger.info("Найдено файлов мемов: %d", len(meme_files))
        if not meme_files:
            await self.update.message.reply_text(constants.NO_MEMES)
            logger.warning("Нет мемов для показа пользователю!")
            return
        for idx, meme_file in enumerate(meme_files, 1):
            file_path = os.path.join(meme_dir, meme_file)
            try:
                with open(file_path, "rb") as photo:
                    callback_data = f"select_meme:{meme_file}"
                    logger.info(f"Создаём кнопку с callback_data={callback_data}")
                    keyboard = InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    constants.MEME_CHOOSE_BTN + " 💦",
                                    callback_data=callback_data,
                                )
                            ]
                        ]
                    )
                    caption = (
                        texts.MEME_CAPTION(idx, os.path.splitext(meme_file)[0])
                        + "\nВыбери, если не боишься стать легендой! 🤠"
                    )
                    await self.update.message.reply_photo(
                        photo=photo, caption=caption, reply_markup=keyboard
                    )
                    logger.info("Отправлен мем: %s (idx=%d)", meme_file, idx)
            except Exception as e:
                logger.error("Ошибка при отправке мема %s: %s", meme_file, e)
