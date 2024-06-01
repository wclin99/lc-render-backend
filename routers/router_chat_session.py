from typing import Annotated
from fastapi import Body, Depends, Query
from sqlmodel import Session
from lib.chat.chat_session import delete_chat_session
from lib.db import DbEngine
from lib.chat import create_chat_session, get_all_chat_session
from lib.model import ResponseModel
from fastapi import APIRouter

router = APIRouter()


@router.post("/post/", response_model=ResponseModel)
async def post_chat_session(
    user_id: Annotated[str, Body(examples=["user_2dLi29nRiCMsSk8uuEBjK2aek3f"])],
    session: Session = Depends(DbEngine.get_session),
):
    res = create_chat_session(user_id, session)
    return res


@router.get("/get/", response_model=ResponseModel)
async def get_chat_session(
    user_id: Annotated[
        str,
        Query(
            description="user id like: user_2dLi29nRiCMsSk8uuEBjK2aek3f",
            examples=["user_2dLi29nRiCMsSk8uuEBjK2aek3f"],
        ),
    ],
    session: Session = Depends(DbEngine.get_session),
):

    res = get_all_chat_session(user_id, session)
    return res


@router.delete("/delete/", response_model=ResponseModel)
async def del_chat_session(
    user_id: Annotated[str, Body(examples=["user_2dLi29nRiCMsSk8uuEBjK2aek3f"])],
    chat_session_id: Annotated[
        str, Body(examples=["5cc22949-e0f2-40c3-ac0a-889315a195a0"])
    ],
    session: Session = Depends(DbEngine.get_session),
):

    res = delete_chat_session(
        user_id=user_id, chat_session_id=chat_session_id, session=session
    )
    return res
