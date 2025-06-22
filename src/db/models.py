# Models module for database entities

from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class UserState(Base):
    """
    SQLAlchemy ORM model for user state (selected meme, sticker set, etc).

    Attributes:
        id (int): State identifier.
        user_id (int): User identifier.
        meme (str): Selected meme.
        sticker_set_name (str): Name of the sticker set.
    """

    __tablename__ = "user_state"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    meme = Column(String, nullable=True)
    sticker_set_name = Column(String, nullable=True)

    def __repr__(self) -> str:
        return f"UserState(id={self.id}, user_id={self.user_id}, meme={self.meme})"


def get_user_state(session: Session, user_id: int) -> Optional["UserState"]:
    """
    Get the state of a user by user_id.

    Args:
        session (Session): SQLAlchemy session.
        user_id (int): User ID.

    Returns:
        Optional[UserState]: User state object or None.
    """
    return session.query(UserState).filter_by(user_id=user_id).first()


def set_user_state(
    session: Session,
    user_id: int,
    meme: Optional[str] = None,
    sticker_set_name: Optional[str] = None,
) -> "UserState":
    """
    Set or update the state of a user.

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
        user_state = UserState(
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
        user_id (int): User ID.
    """
    user_state = get_user_state(session, user_id)
    if user_state is not None:
        session.delete(user_state)
        session.commit()
