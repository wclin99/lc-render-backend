from sqlmodel import Session, select
import uuid
from lib.db import User_chat_session

from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from lib.model import ResponseModel


def create_chat_session(user_id: str, session: Session):
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



    # 返回响应
    return response_model


def get_all_chat_session(user_id: str, session: Session):
    """
    获取指定用户的全部聊天会话信息。
    
    参数:
    - user_id: str, 用户的唯一标识符。
    - session: Session, 数据库会话实例。
    
    返回值:
    - JSONResponse, 包含聊天会话信息的响应对象。
    """
    try:
        # 构造查询语句，获取指定用户的所有聊天会话
        query_statement = select(User_chat_session).where(
            User_chat_session.user_id == user_id
        )

        # 执行查询并获取结果
        results = session.exec(query_statement).all()

        # 根据查询结果数量，准备响应信息
        if not results:
            record_count = 0
            message = "No rows found."
        elif len(results) == 1:
            message = "1 row found."
        else:
            record_count = len(results)
            message = f"{record_count} rows found."

        # 构造成功响应数据
        response_data = {"message": message, "data": results}
        response_model = ResponseModel(
            success=True, status_code=status.HTTP_200_OK, data=response_data
        )

    except HTTPException as http_exception:
        # 处理HTTP异常，构造失败响应数据
        response_model = ResponseModel(
            success=False,
            status_code=http_exception.status_code,
            error=http_exception.detail,
        )

    except SQLAlchemyError as e:
        # 处理数据库操作异常，构造失败响应数据
        response_model = ResponseModel(
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=str(e),
        )

    # 返回响应数据
    return response_model


def delete_chat_session(user_id: str, chat_session_id: str, session: Session):
    """
    删除指定用户的聊天会话记录。

    参数:
    - user_id: 用户ID，类型为字符串。
    - chat_session_id: 聊天会话ID，类型为字符串。
    - session: 数据库会话实例，用于执行数据库操作。

    返回值:
    - JSONResponse: 包含操作结果信息的JSON响应对象。
    """
    try:
        # 构造SQL查询语句，删除指定用户ID和会话ID的聊天记录
        query_statement = select(User_chat_session).where(
            User_chat_session.user_id == user_id,
            User_chat_session.chat_session_id == chat_session_id,
        )

        # 执行查询并获取结果
        results = session.exec(query_statement).all()

        record_count = len(results)
        if record_count == 0:
            # 如果未找到指定的聊天记录，则抛出HTTP异常
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User_chat_session not found",
            )

        # 根据删除的记录数量，设置反馈信息
        if record_count == 1:
            message = f"1 row deleted."
        else:
            message = f"{record_count} rows deleted."

        # 遍历结果集，将每条记录标记为删除
        for result in results:
            session.delete(result)

        # 提交事务，使删除操作生效
        session.commit()

        # 构造成功响应数据
        response_data = {"message": message, "data": results}
        response_model = ResponseModel(
            success=True, status_code=status.HTTP_200_OK, data=response_data
        )

    except HTTPException as http_exception:
        # 如果捕获到HTTP异常，构造失败响应数据
        response_model = ResponseModel(
            success=False,
            status_code=http_exception.status_code,
            error=http_exception.detail,
        )

    except SQLAlchemyError as e:
        # 如果数据库操作失败，构造失败响应数据
        response_model = ResponseModel(
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error=str(e),
        )


    # 返回响应数据
    return response_model
