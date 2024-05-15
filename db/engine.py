import threading
from typing import Literal, Union
from sqlalchemy import Engine, true
from sqlmodel import SQLModel, Session, create_engine
import uuid
from psycopg import Connection as PsycopgConnection

class DbEngine:

    _instance = None
    _lock = threading.Lock()
    _conn_str = None
    _session_id = None
    _psycopg_conn = None

    @classmethod
    def init_db(cls):
        SQLModel.metadata.create_all(cls.get_instance())

    @classmethod
    def get_instance(cls) -> Engine:

        with cls._lock:
            if cls._instance is None:

                cls._conn_str = "postgresql://dev:Ab4w0gMRCLiH@ep-cold-fog-a1g5sf87.ap-southeast-1.aws.neon.tech/dev"

                eng = create_engine(
                    cls._conn_str,
                    connect_args={
                        "sslmode": "require",
                    },
                    pool_recycle=300,
                    # echo=True,
                )
                cls._instance = eng
            return cls._instance
        

    @classmethod
    def get_psycopg_conn(cls) -> PsycopgConnection:
        if cls._psycopg_conn is None:
            cls._psycopg_conn = PsycopgConnection.connect(cls.get_connection_id())
        return cls._psycopg_conn

    @classmethod
    def get_session_id(cls):
        if cls._session_id is None:
            cls._session_id = str(uuid.uuid4())
        return cls._session_id

    @classmethod
    def get_connection_id(cls):
        return cls._conn_str

    @classmethod
    def get_session(cls):
        cls.get_session_id()
        with Session(cls.get_instance()) as session:
            yield session
