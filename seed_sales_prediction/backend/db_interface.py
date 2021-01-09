#!python3
# -*- coding: utf-8 -*-
"""An interface for communicating with SQL database."""
from typing import ContextManager
import contextlib

from sqlalchemy import orm, create_engine

from seed_sales_prediction.backend.database_schema import Base
from seed_sales_prediction.settings import DATABASE, DEBUG


def get_session(do_create=True) -> ContextManager[orm.session.Session]:
    """
    A context manager for communication with SQL database. Automatically create all tables which dont currently exist
    when this function is envoked. Automatically commit changes to database and rollback if an error occurs.
    """
    eng = create_engine(DATABASE, echo=DEBUG)
    if do_create:
        Base.metadata.create_all(eng)
    sm = orm.session.sessionmaker(eng)

    @contextlib.contextmanager
    def managed_sm() -> ContextManager[orm.session.Session]:
        sess = sm()  # type: orm.session.Session
        try:
            yield sess  # type: orm.session.Session
            sess.commit()
        except:
            sess.rollback()
            raise
        finally:
            sess.close()

    return managed_sm()