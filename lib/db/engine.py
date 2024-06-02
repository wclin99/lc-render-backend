import threading
from typing import Literal, Union
from sqlalchemy import Engine, true
from sqlmodel import SQLModel, Session, create_engine
import uuid
import psycopg2 

class DbEngine:
    """
    DbEngine 类用于管理数据库连接和会话。
    使用单例模式确保全局仅有一个数据库引擎实例。
    支持异步操作的数据库连接。
    """

    _instance = None
    _lock = threading.Lock()  # 用于确保线程安全地初始化单例
    _conn_str :Union[str,None]= None          # 存储数据库连接字符串
    _session_id :Union[str,None]= None        # 存储会话ID，用于追踪和管理会话
    _psycopg_conn = None      # 存储Psycopg（PostgreSQL库）的连接对象

    @classmethod
    def init_db(cls,*,conn_str:str):
        """
        初始化数据库模式，即创建所有表。
        """
        SQLModel.metadata.create_all(cls.get_instance(conn_str=conn_str))  # 创建或更新数据库模式

    @classmethod
    def get_instance(cls,*,conn_str:str) -> Engine:
        """
        获取数据库引擎的实例。
        
        返回值:
            Engine: 数据库引擎的实例。
        """
        with cls._lock:  # 确保线程安全地初始化单例
            if cls._instance is None or cls._conn_str != conn_str:
                # 初始化数据库连接字符串
                cls._conn_str = conn_str
                
                cls._session_id=None
                cls._psycopg_conn = None
                
                # 创建数据库引擎实例，配置SSL模式和连接池回收时间
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
    def get_psycopg_conn(cls) :
        """
        获取Psycopg2数据库连接。
        
        返回值:
            PsycopgConnection: Psycopg2的数据库连接对象。
        """
        if cls._psycopg_conn is None:
            cls._psycopg_conn = psycopg2.connect(cls.get_connection_id())  # 获取并创建数据库连接
        return cls._psycopg_conn

    @classmethod
    def get_session_id(cls):
        """
        获取或生成会话ID。
        
        返回值:
            str: 会话的唯一标识符。
        """
        if cls._session_id is None:
            cls._session_id = str(uuid.uuid4())  # 随机生成UUID作为会话ID
        return cls._session_id

    @classmethod
    def get_connection_id(cls):
        """
        获取数据库连接字符串。
        
        返回值:
            str: 数据库连接字符串。
        """
        return cls._conn_str

    @classmethod
    def get_session(cls):
        """
        获取数据库会话。
        
        返回值:
            session: 一个用于执行数据库操作的会话上下文管理器。
        """
        cls.get_session_id()  # 保证会话ID被初始化
        with Session(cls.get_instance(conn_str=cls._conn_str)) as session:  # 创建会话实例
            yield session  # 提供一个会话对象，供用户在with语句块中使用