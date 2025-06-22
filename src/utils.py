"""
Utility functions for the memfaceswap project.
RecallDev style: SOLID, PEP 8, only module imports, type hints, Google-style docstrings, flat code.
"""

from typing import Any

import src.services as services


def get_effective_message(update: Any, context: Any) -> Any:
    """
    Universal function to get the message object from update/context.
    Универсальная функция для получения объекта message из update/context.

    Args:
        update: telegram update
        context: telegram context

        Returns:
            message object
    """
    if hasattr(update, "message") and update.message:
        return update.message
    if hasattr(update, "edited_message") and update.edited_message:
        return update.edited_message
    if hasattr(update, "callback_query") and update.callback_query:
        return update.callback_query.message
    if hasattr(context, "message") and context.message:
        return context.message
    return None
