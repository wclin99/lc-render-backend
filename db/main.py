import threading
from typing import Literal, Union
from sqlalchemy import Engine, true
from sqlmodel import SQLModel, Session, create_engine


class DbEngine:

    _instance = None
    _lock = threading.Lock()


    @classmethod
    def init_db(cls):
       SQLModel.metadata.create_all(cls.get_instance())

    @classmethod
    def get_instance(cls) -> Engine:

        with cls._lock:
            if cls._instance is None:

                eng = create_engine(
                    "postgresql://dev:Ab4w0gMRCLiH@ep-cold-fog-a1g5sf87.ap-southeast-1.aws.neon.tech/dev",
                    connect_args={
                        "sslmode": "require",
                    },
                    pool_recycle=300,
                    # echo=True,
                )
                cls._instance = eng
            return cls._instance
        
    @classmethod
    def get_session(cls):
        with Session(cls.get_instance()) as session:
            yield session  





