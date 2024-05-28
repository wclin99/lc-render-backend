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


class Chat_history_new(SQLModel, table=True):

    id: Optional[int] = Field(default=None, primary_key=True)

    # 会话 ID，用于区分不同的数据库通信会话
    # 这里叫做 session_id，而不是chat_session_id
    # 是因为 PostgresChatMessageHistory 中对于这个字段就是这样定义
    # 因此 ORM 的定义只能妥协
    session_id: str

    # 聊天消息内容，以JSONB格式存储，可以包含丰富的信息
    message: str

    # 消息创建时间，使用DateTime类型以确保时间和数据库的一致性和查询效率
    # 这里需要是 Optional[datetime] 而不是 datetime
    # 因为在调试的时候，PostgresChatMessageHistory的 add_messages方法不会添加时间
    # 如果是 datetime 则会报错，违背非空约束
    # 因此这里只能 Optional[datetime] ，然后在其他代码添加时间
    created_at: Optional[datetime] = Field(default=datetime.now())


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
