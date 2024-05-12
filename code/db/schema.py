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