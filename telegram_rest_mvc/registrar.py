"""Utilities to register telegram_rest_mvc routes to python-telegram-bot Application."""

from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)

from .router import Router


def register_routes(app: Application, router: Router):
    import logging
    logger = logging.getLogger(__name__)
    for route in router.all_routes():
        if route.kind == "command":
            app.add_handler(CommandHandler(route.pattern.lstrip("/"), route.handler))
            logger.info(f"[REGISTRAR] Registered command: /{route.pattern.lstrip('/')} handler={route.handler} name={route.name}")
        elif route.kind == "callback":
            app.add_handler(CallbackQueryHandler(route.handler, pattern=route.pattern))
            logger.info(f"[REGISTRAR] Registered callback: pattern={route.pattern} handler={route.handler} name={route.name}")
        elif route.kind == "message":
            app.add_handler(
                MessageHandler(filters.TEXT & ~filters.COMMAND, route.handler)
            )
            logger.info(f"[REGISTRAR] Registered message handler: handler={route.handler} name={route.name}")
        elif route.kind == "photo":
            app.add_handler(
                MessageHandler(filters.PHOTO & ~filters.COMMAND, route.handler)
            )
            logger.info(f"[REGISTRAR] Registered photo handler: handler={route.handler} name={route.name}")
        else:
            logger.warning(f"[REGISTRAR] Unknown route kind: {route.kind} pattern={route.pattern} handler={route.handler} name={route.name}")
