import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import src.db.models as models
import src.db.services as user_state

DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def sync_session():
    engine = create_engine(DATABASE_URL, echo=False)
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()

def test_user_state_crud(sync_session):
    # Create
    user_state.set_user_state(sync_session, 123, meme="meme1", sticker_set_name="set1")
    user = user_state.get_user_state(sync_session, 123)
    assert user is not None
    assert user.user_id == 123
    assert user.sticker_set_name == "set1"
    assert user.meme == "meme1"
    # Update
    user_state.set_user_state(sync_session, 123, meme="meme2")
    updated = user_state.get_user_state(sync_session, 123)
    assert updated.meme == "meme2"
    # Delete
    user_state.clear_user_state(sync_session, 123)
    deleted = user_state.get_user_state(sync_session, 123)
    assert deleted is None

def test_user_state_repr(sync_session):
    user_state.set_user_state(sync_session, 1, meme="reprmeme", sticker_set_name="reprset")
    user = user_state.get_user_state(sync_session, 1)
    rep = repr(user)
    assert rep.startswith("UserState(") and "user_id=1" in rep and "reprmeme" in rep

def test_set_user_state_update_sticker_only(sync_session):
    user_state.set_user_state(sync_session, 2, meme="m", sticker_set_name="s1")
    user_state.set_user_state(sync_session, 2, sticker_set_name="s2")
    user = user_state.get_user_state(sync_session, 2)
    assert user.sticker_set_name == "s2"
    assert user.meme == "m"

def test_set_user_state_update_both_fields(sync_session):
    user_state.set_user_state(sync_session, 3, meme="m1", sticker_set_name="s1")
    user_state.set_user_state(sync_session, 3, meme="m2", sticker_set_name="s2")
    user = user_state.get_user_state(sync_session, 3)
    assert user.meme == "m2"
    assert user.sticker_set_name == "s2"

def test_set_user_state_no_update(sync_session):
    user_state.set_user_state(sync_session, 4, meme="m", sticker_set_name="s")
    user_state.set_user_state(sync_session, 4)
    user = user_state.get_user_state(sync_session, 4)
    assert user.meme == "m"
    assert user.sticker_set_name == "s"

def test_get_user_state_not_found(sync_session):
    user = user_state.get_user_state(sync_session, 999)
    assert user is None

def test_clear_user_state_not_found(sync_session):
    # Should not raise
    user_state.clear_user_state(sync_session, 888)
    assert user_state.get_user_state(sync_session, 888) is None

    # Create
    user_state.set_user_state(sync_session, 123, meme="meme1", sticker_set_name="set1")
    user = user_state.get_user_state(sync_session, 123)
    assert user is not None
    assert user.user_id == 123
    assert user.sticker_set_name == "set1"
    assert user.meme == "meme1"
    # Update
    user_state.set_user_state(sync_session, 123, meme="meme2")
    updated = user_state.get_user_state(sync_session, 123)
    assert updated.meme == "meme2"
    # Delete
    user_state.clear_user_state(sync_session, 123)
    deleted = user_state.get_user_state(sync_session, 123)
    assert deleted is None
