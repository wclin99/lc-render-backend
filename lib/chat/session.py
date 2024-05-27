from sqlmodel import  Session,  select
import uuid
from lib.db import  User_chat_session


def create_chat_session(user_id: str, session: Session):

    chat_session_id = str(uuid.uuid4())

    user_chat_session = User_chat_session(
        user_id=user_id, chat_session_id=chat_session_id
    )

    session.add(user_chat_session)

    session.commit()
    session.refresh(user_chat_session)

    return chat_session_id


def get_chat_session(user_id: str, session: Session):

    query_statement = select(User_chat_session).where(
        User_chat_session.user_id == user_id
    )

    results =  session.exec(query_statement).all()

    return results

    



# def delete_chat_session():
# 删除指定会话
# 返回更新结果及更新后的回话id列表
