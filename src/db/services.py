"""
Database-related services for user state management.
All comments must be in English. Follows PEP 8 and Google-style docstrings.
"""

from typing import Optional

from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine

engine = create_engine("sqlite:///memfaceswap.db", echo=False, future=True)
SessionLocal = sessionmaker(bind=engine)

def get_session():
    """
    Returns a new SQLAlchemy session.
    """
    return SessionLocal()

import src.db.models as models


def get_user_state(session: Session, user_id: int) -> Optional[models.UserState]:
    """
    Retrieves the user state by user_id.

    Args:
        session (Session): SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        Optional[UserState]: User state object or None if not found.
    """
    return session.query(models.UserState).filter_by(user_id=user_id).first()


def set_user_state(
    session: Session,
    user_id: int,
    meme: Optional[str] = None,
    sticker_set_name: Optional[str] = None,
) -> models.UserState:
    """
    Sets or updates the user state.

    Args:
        session (Session): SQLAlchemy session.
        user_id (int): User ID.
        meme (Optional[str]): Meme file name.
        sticker_set_name (Optional[str]): Sticker set name.

    Returns:
        UserState: Updated user state object.
    """
    user_state = get_user_state(session, user_id)
    if user_state is None:
        user_state = models.UserState(
            user_id=user_id, meme=meme, sticker_set_name=sticker_set_name
        )
        session.add(user_state)
    else:
        if meme is not None:
            user_state.meme = meme
        if sticker_set_name is not None:
            user_state.sticker_set_name = sticker_set_name
    session.commit()
    return user_state


def clear_user_state(session: Session, user_id: int) -> None:
    """
    Clears the user state (removes the record).

    Args:
        session (Session): SQLAlchemy session.
        user_id (int): Telegram user ID.
    """
    user_state = get_user_state(session, user_id)
    if user_state:
        session.delete(user_state)
        session.commit()
