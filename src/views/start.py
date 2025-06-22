"""
View для команды /start.
Стиль RecallDev: только import module, type hints, docstrings, flat code.
"""

import logging

import src.constants.texts as texts
from telegram_rest_mvc import views

logger = logging.getLogger(__name__)


class StartView(views.View):
    async def command(self):
        """
        Обрабатывает команду /start, логирует этапы.
        """
        logger.info(
            "/start command called for user_id=%s",
            getattr(self.update.effective_user, "id", None),
        )
        try:
            await self.update.message.reply_text(texts.GACHIMUCHI_GREETING)
            logger.info("Приветствие отправлено пользователю.")
        except Exception as e:
            logger.error("Ошибка при отправке приветствия: %s", e)
