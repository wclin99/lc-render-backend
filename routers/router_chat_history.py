from fastapi import APIRouter

from typing import Annotated
from fastapi import Depends, Query, Body
from sqlmodel import Session
from lib.db import DbEngine
from lib.chat import ChatHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from lib.model import ResponseModel, ChatRole

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

    message_class = {
        ChatRole.system: SystemMessage,
        ChatRole.ai: AIMessage,
        ChatRole.human: HumanMessage,
    }.get(role, None)

    if message_class is None:
        raise ValueError(f"Invalid role: {role}")

    message = message_class(content=content)

    return ChatHistory.add_chat_messages(
        [message],
        session,
        chat_session,
    )


@router.get("/get/", response_model=ResponseModel)
def get_chat_history(
    chat_session: Annotated[
        str,
        Query(
            pattern="^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$",
            description="uuid like: 5cc22949-e0f2-40c3-ac0a-889315a195a0",
            examples=["5cc22949-e0f2-40c3-ac0a-889315a195a0"]
        ),
    ],
    session: Session = Depends(DbEngine.get_session),
):

    return ChatHistory.get_chat_message(session=session, chat_session_id=chat_session)
