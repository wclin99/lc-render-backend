from typing import Union, Sequence
from langchain_postgres import PostgresChatMessageHistory
from sqlmodel import Session, select
import uuid
from lib.db import Chat_history as ChatHistoryTable

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from lib.model import ResponseModel
from lib.db import Chat_history, DbEngine
import threading
from langchain_core.messages import BaseMessage


class ChatHistory:
    """
    聊天历史记录类，用于管理和存储聊天会话的历史消息。
    本类实现为单例模式，确保在整个应用中只有一个实例。
    """

    # 存储ChatHistory的实例
    _instance: PostgresChatMessageHistory = None

    # 用于确保线程安全地初始化单例
    _lock = threading.Lock()

    # 存储当前聊天会话的ID
    _chat_session_id = None

    @classmethod
    def init(cls, chat_session_id:str) -> PostgresChatMessageHistory:
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

        cls._chat_session_id = chat_session_id  # 存储会话ID

        # 初始化PostgresChatMessageHistory实例
        cls._instance = PostgresChatMessageHistory(
            ChatHistoryTable.__name__.lower(),
            cls._chat_session_id,
            sync_connection=DbEngine.get_psycopg_conn(),
        )

        return cls._instance

    @classmethod
    def get_instance(
        cls, chat_session_id: Union[str, None]
    ) -> PostgresChatMessageHistory:
        """
        获取ChatHistory的实例。如果实例不存在，则通过init方法初始化。

        参数:
            chat_session_id (str): 聊天会话的唯一标识符。

        返回:
            PostgresChatMessageHistory: ChatHistory的实例。
        """
        with cls._lock:  # 确保线程安全地获取或初始化实例

            if cls._instance is None:
                # 如果chat_session_id为空，则抛出异常
                if chat_session_id is None:
                    raise ValueError("chat_session_id is required")

                cls._instance = cls.init(chat_session_id)  # 初始化实例

            return cls._instance

    # def get_chat_message(cls):
    #     """
    #     获取聊天历史消息。

    #     返回:
    #         聊天历史消息。
    #     """
    #     return cls._instance.get_messages()

    # def add_chat_message(cls, messages: Sequence[BaseMessage]):
    #     """
    #     添加消息到聊天历史记录。

    #     参数:
    #         messages (Sequence[BaseMessage]): 要添加的消息序列。
    #     """
    #     cls._instance.add_messages(messages)  # 添加消息
