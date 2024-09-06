from contextlib import ContextDecorator
from contextlib import AbstractContextManager
from sqlalchemy.orm import sessionmaker, scoped_session, Session as SessionType
from typing import Optional, TypeVar, Type, Any
from types import TracebackType
import db.models as db_models
from sqlalchemy import create_engine
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shabzak.db')
db_engine = create_engine(f'sqlite:////{DB_PATH}', echo=True)
db_models.Base.metadata.create_all(db_engine)

T = TypeVar('T', bound=Optional[Type[BaseException]])

SessionFactory = sessionmaker(bind=db_engine)
Session = scoped_session(SessionFactory)

class DBSession(ContextDecorator, AbstractContextManager[SessionType]):
    
    def __enter__(self) -> SessionType:
        self.session = Session()
        return self.session

    def __exit__(self, exc_type: T, exc_value: Optional[BaseException], traceback: Optional[TracebackType]) -> None:
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()
        Session.remove()
