from datetime import datetime
from typing import Union, Sequence
from langchain_postgres import PostgresChatMessageHistory
from sqlmodel import Session, select
import uuid
from lib.db import Chat_history_new as ChatHistoryTable

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from lib.model import ResponseModel
from lib.db import Chat_history_new, DbEngine
import threading
from langchain_core.messages import BaseMessage
from psycopg2 import errors as pg_errors


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
    def __init_ch(cls, chat_session_id: str) -> PostgresChatMessageHistory:
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
            cls._chat_session_id = chat_session_id  # 存储会话ID
            cls._instance = PostgresChatMessageHistory(
                ChatHistoryTable.__name__.lower(),
                cls._chat_session_id,
                sync_connection=DbEngine.get_psycopg_conn(),
            )
        except pg_errors.OperationalError as e:
            # 处理数据库连接异常
            raise ValueError("Failed to connect to the database.") from e

        return cls._instance
    



    @classmethod
    def __has_instance(cls, chat_session_id: Union[str, None] = None) -> bool:
        """
        判断ChatHistory的实例是否已创建。如果实例不存在，则通过init方法初始化。
        
        参数:
            chat_session_id (str): 聊天会话的唯一标识符。如果为None，并且当前没有实例存在，函数将返回False。
        
        返回:
            bool: 如果实例存在返回True，否则返回False。
        """
        with cls._lock:  # 确保线程安全地获取或初始化实例
            # 检查当前是否有实例存在
            if cls._instance is None:  
                # 如果chat_session_id为空，则直接返回False
                if chat_session_id is None:
                    return False
                # 初始化实例
                cls._instance = cls.__init_ch(chat_session_id)  
            
            # 如果传入的chat_session_id与当前实例的chat_session_id不一致，重新初始化实例
            if chat_session_id is not cls._chat_session_id:
                cls._instance = cls.__init_ch(chat_session_id)
            
            return bool(cls._instance)
        


    @classmethod
    def get_chat_message(
        cls, chat_session_id: Union[str, None] = None
    ) -> ResponseModel:
        """
        获取聊天历史消息。

        返回:
            聊天历史消息。
        """
        try:
            
            if not cls.__has_instance(chat_session_id):
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
                )
            
            results = cls._instance.get_messages()

            # 操作成功，构造成功响应数据
            message = "success."
            response_data = {"message": message, "data": results}
            response_model = ResponseModel(
                success=True, status_code=status.HTTP_200_OK, data=response_data
            )

        except HTTPException as http_exception:
            # 捕获HTTP异常，构造失败响应数据
            response_model = ResponseModel(
                success=False,
                status_code=http_exception.status_code,
                error=http_exception.detail,
            )

        except SQLAlchemyError as e:
            # 捕获数据库操作异常，构造失败响应数据
            response_model = ResponseModel(
                success=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error=str(e),
            )

        # 返回响应
        return response_model
    




    @classmethod
    def add_chat_messages(
        cls, messages: Sequence[BaseMessage], session: Session,chat_session_id: Union[str, None] = None
    ) -> ResponseModel:
        """
        添加消息到聊天历史记录。

        参数:
            messages (Sequence[BaseMessage]): 要添加的消息序列。
        """

        try:
            
            if not cls.__has_instance(chat_session_id):
              raise HTTPException(
                  status_code=status.HTTP_404_NOT_FOUND, detail="Chat session not found"
              )

            cls._instance.add_messages(messages)  # 添加消息

            # 查询表中所有创建时间为空的记录
            query_statement = select(Chat_history_new).where(
                Chat_history_new.created_at == None
            )
            # 获取所有时间为空的记录
            results = session.exec(query_statement).all()

            for result in results:
                # 使用sqlmodel，为这些记录的created_at更新为当前时间datetime.now()
                result.created_at = datetime.now()

            session.commit()

            # 操作成功，构造成功响应数据
            message = "success."
            response_data = {"message": message, "data": results}
            response_model = ResponseModel(
                success=True, status_code=status.HTTP_200_OK, data=response_data
            )

        except HTTPException as http_exception:
            # 捕获HTTP异常，构造失败响应数据
            response_model = ResponseModel(
                success=False,
                status_code=http_exception.status_code,
                error=http_exception.detail,
            )

        except SQLAlchemyError as e:
            # 捕获数据库操作异常，构造失败响应数据
            response_model = ResponseModel(
                success=False,
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                error=str(e),
            )

        # 返回响应
        return response_model
