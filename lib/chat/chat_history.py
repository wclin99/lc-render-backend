from sqlmodel import Session, select
import uuid
from lib.db import Chat_history

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from lib.model import ResponseModel



def add_chat_session(user_id: str, session: Session):
    """
    创建一个新的聊天会话。

    参数:
    user_id (str): 用户的唯一标识符。
    session (Session): 数据库会话实例。

    返回:
    JSONResponse: 包含操作结果的JSON响应对象。
    """

    # 生成唯一的会话ID
    chat_session_id = str(uuid.uuid4())

    # 创建用户聊天会话对象
    user_chat_session = User_chat_session(
        user_id=user_id, chat_session_id=chat_session_id
    )

    try:

        session.add(user_chat_session)
        session.commit()
        session.refresh(user_chat_session)

        # 操作成功，构造成功响应数据
        message = "success."
        response_data = {"message": message, "data": user_chat_session}
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

    finally:
        # 确保数据库会话关闭
        session.close()

    # 返回响应
    return response_model
