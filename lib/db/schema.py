from typing import Annotated, Union, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select, DateTime, Uuid
from datetime import datetime


class Todo(SQLModel, table=True):
    """
    Todo 类表示一个待办事项，继承自 SQLModel 以支持与数据库的交互。

    属性:
    - id: 待办事项的唯一标识符，为整数类型。如果未指定，则为 None，是主键。
    - content: 待办事项的内容，为字符串类型，并建立了索引以支持快速查询。
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


class Chat_history(SQLModel, table=True):
    # 使用Integer类型并去掉Optional，因为这是主键，SQLAlchemy会处理自增
    id: Optional[int] = Field(default=None, primary_key=True)
    # 会话ID，用于区分不同的数据库通信会话
    session_id: str
    # 用户ID，用于区分不同的用户
    # user_id: str
    # 聊天消息内容，以JSONB格式存储，可以包含丰富的信息
    message: str
    # 消息创建时间，使用DateTime类型以确保时间和数据库的一致性和查询效率
    created_at: datetime = Field(default=datetime.now())


class User_chat_session(SQLModel, table=True):
    """
    UserSession 类表示用户的会话，继承自 SQLModel 以支持与数据库的交互。

    属性:
    - id: 用户会话的唯一标识符，为整数类型，如果未指定，则为 None，是主键。
    - user_id: 用户 ID，为字符串类型，与用户表中的 ID 对应。
    - session_id: 会话 ID，为字符串类型，用于唯一标识一个会话。
    - created_at: 记录创建时间，为 DateTime 类型，使用默认值为当前时间。
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: str
    chat_session_id: str
    created_at: datetime = Field(default=datetime.now())
