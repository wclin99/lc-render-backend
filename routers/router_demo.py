from fastapi import APIRouter
from sqlmodel import Session, distinct, select
from lib.db import User_chat_session,Chat_history_new
from fastapi import  Depends, Query, Request, Body, status
from lib.db import DbEngine
from fastapi.responses import HTMLResponse

router = APIRouter()



@router.get("/")
async def debug(request: Request):
    return HTMLResponse(
        content=open("templates/index.html", "rb").read(), status_code=200
    )




@router.get("/fetch_all_user_ids/")
async def fetch_all_user_ids(session: Session = Depends(DbEngine.get_session)):
    
    statement = select(distinct(User_chat_session.user_id))
    result = session.exec(statement)
    unique_user_ids = result.all()
    return unique_user_ids



@router.get('/fetch_sessions_by_user_id')
def fetch_sessions_by_user_id(user_id: str, session: Session = Depends(DbEngine.get_session)):
  
    statement = select(User_chat_session.chat_session_id).where(User_chat_session.user_id == user_id)
    result = session.exec(statement).all()
    return result


@router.get("/fetch_messages_by_session_id/")
def fetch_messages_by_session_id(session_id: str, session: Session = Depends(DbEngine.get_session)):
  
    statement = select(Chat_history_new.message).where(Chat_history_new.session_id == session_id)
    result = session.exec(statement).all()
    return result
