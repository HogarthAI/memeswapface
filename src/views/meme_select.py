"""
View для обработки выбора мема пользователем через callback.
Стиль RecallDev: только import module, type hints, docstrings, flat code.
"""

import logging

import src.constants.constants as constants
import src.constants.texts as texts
import src.db.services as db_services
import src.db.services as user_state
import src.utils as utils
from telegram_rest_mvc import views

logger = logging.getLogger(__name__)


class MemeSelectView(views.View):
    """
    View-класс для обработки выбора мема пользователем.
    """

    async def command(self) -> None:
        """
        Заглушка для совместимости с MVC. Не используется, так как MemeSelectView работает только через callback.
        """
        pass

    async def callback(self, meme_file: str = None) -> None:
        """
        Обработка выбора мема пользователем и установка состояния. Логирует этапы.
        meme_file: опционально для тестов, если не передан — берётся из update.callback_query
        """
        user_id = getattr(self.update.effective_user, "id", None)
        logger.info("callback MemeSelectView вызван для user_id=%s", user_id)
        try:
            if meme_file is None:
                meme_file = self.update.callback_query.data.split(":", 1)[1]
            logger.info("Пользователь выбрал мем: %s", meme_file)
            with db_services.get_session() as session:
                user_state.set_user_state(session, user_id, meme_file)
            message = utils.get_effective_message(self.update, self.context)
            await message.reply_text(texts.MEME_SELECTED(meme_file))
            logger.info("Ответ пользователю отправлен.")
        except Exception as e:
            logger.error("Ошибка в MemeSelectView.callback: %s", e)
