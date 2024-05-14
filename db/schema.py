from typing import Annotated, Union, Optional

from sqlmodel import Field, Session, SQLModel, create_engine, select


class Todo(SQLModel, table=True):
    """
    Todo 类表示一个待办事项，继承自 SQLModel 以支持与数据库的交互。

    属性:
    - id: 待办事项的唯一标识符，为整数类型。如果未指定，则为 None，是主键。
    - content: 待办事项的内容，为字符串类型，并建立了索引以支持快速查询。
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)


class ChatHistory(SQLModel, table=True):
    # 使用Integer类型并去掉Optional，因为这是主键，SQLAlchemy会处理自增
    id: Optional[int]  = Field(default=None, primary_key=True)
    # 会话ID，用于区分不同的聊天会话
    session_id: str
    # 聊天消息内容，以JSONB格式存储，可以包含丰富的信息
    message: str
    # 消息创建时间，使用DateTime类型以确保时间和数据库的一致性和查询效率
    created_at: DateTime = Field(default=datetime.now)
