from fastapi import APIRouter

from typing import Annotated
from fastapi import Depends, Query, Body
from sqlmodel import Session
from lib.db import DbEngine
from lib.chat import ChatHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from lib.model import ResponseModel, ChatRole
import json
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


router = APIRouter()


@router.post("/post/", response_model=ResponseModel)
def post_chat_history(
    chat_session: Annotated[
        str, Body(examples=["5cc22949-e0f2-40c3-ac0a-889315a195a0"])
    ],
    role: Annotated[ChatRole, Body(examples=["system, ai, or human"])],
    content: Annotated[str, Body(examples=["Some chat messages here..."])],
    session: Session = Depends(DbEngine.get_session),
):
    try:
        message_class = {
            ChatRole.system: SystemMessage,
            ChatRole.ai: AIMessage,
            ChatRole.human: HumanMessage,
        }.get(role, None)

        if message_class is None:
            raise ValueError(f"Invalid role: {role}")

        message = message_class(content=content)

        response_data = ChatHistory.add_chat_messages(
            [message],
            session,
            chat_session,
        )

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


@router.get("/get/", response_model=ResponseModel)
def get_chat_history(
    chat_session: Annotated[
        str,
        Query(
            pattern="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
            description="uuid like: 5cc22949-e0f2-40c3-ac0a-889315a195a0",
            examples=["5cc22949-e0f2-40c3-ac0a-889315a195a0"],
        ),
    ],
    session: Session = Depends(DbEngine.get_session),
):

    try:
        message_list = ChatHistory.get_chat_messages(
            session=session, chat_session_id=chat_session
        )

        response_model = ResponseModel(
            success=True,
            status_code=status.HTTP_200_OK,
            data={"messages": message_list},
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

    except json.JSONDecodeError as e:
        # 捕获JSON解析错误
        response_model = ResponseModel(
            success=False,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Error decoding JSON: " + str(e),
        )

    # 返回响应
    return response_model
