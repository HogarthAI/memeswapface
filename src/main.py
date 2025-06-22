import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
import telegram.ext

import db
import src.settings.config as settings_config
import telegram_rest_mvc.registrar
import telegram_rest_mvc.router
from src.router import router

"""
Точка входа для memfaceswap на telegram_rest_mvc.
"""


def main():
    config = settings_config.BaseConfiguration()
    app = telegram.ext.Application.builder().token(config.telegram.token).build()
    telegram_rest_mvc.registrar.register_routes(app, router)
    app.run_polling()


if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)
    main()
