from fastapi import HTTPException
from sqlmodel import Session, select
import uuid
from lib.db import User_chat_session


def create_chat_session(user_id: str, session: Session):

    chat_session_id = str(uuid.uuid4())

    user_chat_session = User_chat_session(
        user_id=user_id, chat_session_id=chat_session_id
    )

    session.add(user_chat_session)

    session.commit()
    session.refresh(user_chat_session)

    return user_chat_session


def get_all_chat_session(user_id: str, session: Session):

    query_statement = select(User_chat_session).where(
        User_chat_session.user_id == user_id
    )

    results = session.exec(query_statement).all()

    return results


def delete_chat_session(user_id: str, chat_session_id: str, session: Session):

    query_statement = select(User_chat_session).where(
        User_chat_session.user_id == user_id,
        User_chat_session.chat_session_id == chat_session_id,
    )

    results = session.exec(query_statement).all()

    record_count = len(results)
    if record_count == 0:
        raise HTTPException(status_code=404, detail="User_chat_session not found")

    message = f"{record_count} row(s) deleted."

    for result in results:
        session.delete(result)

    session.commit()

    return {"status": "success", "message": message}

    # return message
