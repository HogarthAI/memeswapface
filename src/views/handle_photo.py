"""
View для обработки фото пользователя и запуска face swap.
Стиль RecallDev: только import module, type hints, docstrings, flat code.
"""

import logging
import os

import src.bot.flows.face_swap_flow as face_swap_flow
import src.constants.constants as constants
import src.constants.texts as texts
import src.db.services as db_services
import src.utils as utils
from telegram_rest_mvc import views

logger = logging.getLogger(__name__)


class HandlePhotoView(views.View):
    """
    View-класс для обработки входящего фото и запуска пайплайна face swap через flow.
    SOLID: только рендер результата, вся логика — во flow.
    """

    async def command(self) -> None:
        """
        Получает фото пользователя, вызывает бизнес-логику face_swap_flow и рендерит результат. Логирует этапы.
        """
        user_id = getattr(self.update.effective_user, "id", None)
        logger.info("HandlePhotoView.command вызван для user_id=%s", user_id)
        try:
            message = utils.get_effective_message(self.update, self.context)
            imgbb_api_key = os.environ.get("IMGBB_API_KEY")
            maxstudio_api_key = os.environ.get("MAXSTUDIO_API_KEY")
            logger.info("Передаём данные во flow: user_id=%s", user_id)
            # Промежуточные сообщения, как в bot.py
            await self.update.message.reply_text("Загружаю мем и твоё фото на сервер... 🏋️‍♂️")
            result = await face_swap_flow.face_swap_flow(
                update=self.update,
                context=self.context,
                user_id=user_id,
                imgbb_api_key=imgbb_api_key,
                maxstudio_api_key=maxstudio_api_key,
            )
            logger.info("Результат работы flow: %s", result)
            if result.get("stage_msgs"):
                for msg in result["stage_msgs"]:
                    await self.update.message.reply_text(msg)
            if result["status"] == "ok":
                from src.bot.flows.sticker_set_flow import create_or_add_sticker_to_set
                bot_username = (await self.context.bot.get_me()).username
                username = getattr(self.update.effective_user, "username", None)
                sticker_url = await create_or_add_sticker_to_set(
                    context=self.context,
                    update=self.update,
                    user_id=user_id,
                    username=username,
                    bot_username=bot_username,
                    sticker_path=result["sticker_path"],
                )
                await self.update.message.reply_sticker(result["sticker_path"])
                await self.update.message.reply_text(f"Твой стикерпак: {sticker_url}")
                logger.info("Стикер и ссылка на пак отправлены пользователю.")
            else:
                await self.update.message.reply_text(result["error"])
                logger.warning("Ошибка в результате flow: %s", result["error"])
        except Exception as e:
            logger.error("Ошибка в HandlePhotoView.command: %s", e)
            await self.update.message.reply_text(texts.FACE_SWAP_FAIL)


    async def add_sticker(self, context, user_id, set_name, sticker_path, update):
        from telegram import InputSticker

        # Removed direct imports; use texts.STICKER_ADDED and texts.STICKER_ADD_ERR below
        with open(sticker_path, "rb") as sticker_file:
            sticker = InputSticker(
                sticker=sticker_file, emoji_list=["💪"], format="static"
            )
            try:
                await context.bot.add_sticker_to_set(
                    user_id=user_id, name=set_name, sticker=sticker
                )
                await self.update.message.reply_text(texts.STICKER_ADDED(set_name))
                print(f"[DEBUG] Стикер добавлен в пак: {set_name}")
            except Exception as e:
                print(f"[ERROR] Ошибка добавления стикера: {e}")
                await self.update.message.reply_text(texts.STICKER_ADD_ERR(e))
