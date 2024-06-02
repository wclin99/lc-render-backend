from datetime import datetime
from typing import Any, Dict, List, Union, Sequence
from langchain_postgres import PostgresChatMessageHistory
from pydantic import BaseModel
from sqlmodel import Session, select
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from lib.db import Chat_history_new as ChatHistoryTable
import json

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from lib.model import ResponseModel
from lib.db import Chat_history_new, DbEngine
import threading
from langchain_core.messages import BaseMessage
from psycopg2 import errors as pg_errors

from lib.model import ChatRole


class SimpleMessage(BaseModel):
    role: ChatRole
    content: str


class ChatHistory:
    """
    聊天历史记录类，用于管理和存储聊天会话的历史消息。
    本类实现为单例模式，确保在整个应用中只有一个实例。
    """

    # 存储ChatHistory的实例
    _instance: Union["ChatHistory", None] = None

    # 用于确保线程安全地初始化单例
    _lock = threading.Lock()

    def __init__(
        self,
        *,
        chat_session_id: str,
        history_len: Union[int, None] = None,
        session: Session
    ):
        """
        初始化ChatHistory单例。

        参数:
            chat_session_id (str): 聊天会话的唯一标识符。

        返回:
            PostgresChatMessageHistory: 初始化后的ChatHistory实例。
        """
        # 验证chat_session_id是否为字符串类型
        if not isinstance(chat_session_id, str):
            raise ValueError("chat_session_id must be a string")

        # 使用try-except来处理数据库连接异常
        try:
            self._messages: List[Dict[str, Any]] = []
            self._db_session: Session = session
            self._chat_session_id: str = chat_session_id  # 存储会话ID
            self._recent_history_length: int = history_len if history_len else 50
            self._postgres_agent = PostgresChatMessageHistory(
                ChatHistoryTable.__name__.lower(),
                self._chat_session_id,
                sync_connection=DbEngine.get_psycopg_conn(),
            )
        except pg_errors.OperationalError as e:
            # 处理数据库连接异常
            raise ValueError("Failed to connect to the database.") from e

    @classmethod
    def get_instance(cls, chat_session_id: str, session: Session) -> "ChatHistory":
        """
        判断ChatHistory的实例是否已创建。如果实例不存在，则通过init方法初始化。

        参数:
            chat_session_id (str): 聊天会话的唯一标识符。如果为None，并且当前没有实例存在，函数将返回False。

        返回:
            bool: 如果实例存在返回True，否则返回False。
        """
        with cls._lock:  # 确保线程安全地获取或初始化实例
            # 检查当前是否有实例存在
            if (
                cls._instance is not None
                and cls._instance._chat_session_id == chat_session_id
            ):

                return cls._instance

            else:

                cls._instance = ChatHistory(
                    chat_session_id=chat_session_id, session=session
                )
                return cls._instance

    def get_chat_messages_from_db(self) -> List[Dict[str, Any]]:
        """
        获取聊天历史消息。

        返回:
            聊天历史消息。
        """

        # results = cls._instance.get_messages() 这句不行
        # 执行查询并获取结果
        messages = self._db_session.exec(
            select(Chat_history_new.message).where(
                Chat_history_new.session_id == self._chat_session_id
            )
        ).all()

        # 解析消息并提取content和type
        parsed_messages = [json.loads(res) for res in messages]

        self._messages.clear()

        for pm in parsed_messages:
            content = pm["data"]["content"]
            role = pm["type"]

            self._messages.append(SimpleMessage(role=role, content=content))

        return self._messages

    def add_chat_messages_to_db(
        self,
        messages: Sequence[BaseMessage],
    ) :
        """
        添加消息到聊天历史记录。

        参数:
            messages (Sequence[BaseMessage]): 要添加的消息序列。
        """

        print(f"Before adding to DB: {messages}, type: {type(messages)}")


        for msg in messages:
            self._db_session.add(ChatHistoryTable(
                session_id=self._chat_session_id,
                message={"type": msg.type, "data": msg.dict()},
                created_at=datetime.now()
            ))
         
        self._db_session.commit()

        return {"mesages":[{"type": msg.type, "data": msg.dict()} for msg in messages]}

    # todo
    def add_message_to_instance_storage(self, *, role: ChatRole, content: str):
        self._messages.append(SimpleMessage(role=role, content=content))

    # todo
    @classmethod
    def get_sliced_messages(cls):
        if len(cls._messages) <= cls._recent_history_length:
            return cls._messages
        return cls._messages[-cls._recent_history_length]


