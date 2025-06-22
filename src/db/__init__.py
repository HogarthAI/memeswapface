# Init for db package

import sqlalchemy

import src.db.models as models


def init_db(db_url: str = "sqlite:///memfaceswap.db") -> None:
    """
    Initialize the database and create all tables if they do not exist.

    Args:
        db_url (str): Database connection URL. Defaults to SQLite file.
    """
    engine = sqlalchemy.create_engine(db_url, echo=False, future=True)
    models.Base.metadata.create_all(bind=engine)
