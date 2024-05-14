import threading
from typing import Literal, Union
from sqlalchemy import Engine, true
from sqlmodel import SQLModel, create_engine


class DbEngine:

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(cls) -> Engine:

        with cls._lock:
            if cls._instance is None:

                eng = create_engine(
                    "postgresql://dev:Ab4w0gMRCLiH@ep-cold-fog-a1g5sf87.ap-southeast-1.aws.neon.tech/dev",
                    connect_args={"sslmode": "require", "check_same_thread": False},
                    pool_recycle=300,
                    echo=True,
                )
                cls._instance = eng
            return cls._instance


def create_db_and_tables(e: Engine):
    """
    创建数据库表。该函数会根据 Todo 类的定义，在数据库中创建相应的表。
    """
    SQLModel.metadata.create_all(e)
