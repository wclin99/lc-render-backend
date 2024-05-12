import threading
from typing import Literal, Union
from sqlalchemy import Engine
from sqlmodel import SQLModel, create_engine
from ..config import DatabaseConfigs


class DbEngine:

    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get_instance(
        cls,
        db_configs: DatabaseConfigs,
        environment: Union[Literal["dev", "preview", "test", "main"], None] = None,
    ) -> Engine:

        with cls._lock:
            if cls._instance is None:

                conn = db_configs.get_database_url(environment)
                eng = create_engine(
                    conn,
                    connect_args={"sslmode": "require"},
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
