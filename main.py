from functools import lru_cache
from sqlmodel import Session, distinct, select
import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated, List, Union, Optional
from fastapi import FastAPI, Depends, Query, Request, Body, status
from fastapi.middleware.cors import CORSMiddleware
from lib.chat.chat_history import ChatHistory
from lib.db import DbEngine, Todo
from lib.config import app_configs, db_configs, api_configs
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from lib.db import User_chat_session
from lib.model import ResponseModel, ApiDocTags, ChatRole
from routers import router_chat_history, router_chat_session, router_demo
from fastapi.testclient import TestClient
from lib.chat.chat import chatWithHistory
from fastapi.responses import StreamingResponse


# 定义一个异步上下文管理器，用于在 FastAPI 应用的生命周期内执行数据库初始化
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    异步上下文管理器，用于在 FastAPI 应用的生命周期内执行初始化和清理操作。

    参数:
    - app: FastAPI 应用实例。

    返回值:
    - 该函数使用 yield 语句分隔了初始化和清理操作，yield 之前的部分在应用启动时执行，之后的部分在应用停止时执行。
    """
    print("Creating tables..")
    DbEngine.init_db()
    yield


# app = FastAPI()
app = FastAPI(lifespan=lifespan)

app.include_router(
    router_chat_session.router,
    prefix="/chat_session",  # 路由前缀
    tags=[ApiDocTags.chat_session],
)
app.include_router(
    router_chat_history.router,
    prefix="/chat_history",  # 路由前缀
    tags=[ApiDocTags.Chat_history],
)
app.include_router(
    router_demo.router,
    prefix="/demo",
    tags=[ApiDocTags.demo],
)

# 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 允许来自该地址的跨域请求
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 允许的 HTTP 方法
    allow_headers=["*"],  # 允许的 HTTP 头部
)


@app.get("/")
async def read_root():
    # return {"branch": "development"}
    return {"branch": "development", "session_id": DbEngine.get_session_id()}


# 使用 lru_cache 装饰器缓存 get_configs 函数的返回结果
# 函数用于获取配置信息
# @lru_cache
# def get_configs():
#     """
#     获取配置对象的实例。

#     Returns:
#         Configs: 配置信息的实例。
#     """
#     return AppConfigs()


@app.get("/app/info/", tags=[ApiDocTags.app])
async def info():
    # settings: Annotated[AppConfigs, Depends(get_configs)]
    """
    提供应用信息的接口。

    Args:
        settings (Configs): 通过依赖注入获取的配置信息对象。

    Returns:
        dict: 包含应用名称等信息的字典。
    """
    # 返回包含应用名称的信息
    return {
        "app_name": app_configs.app_name,
        # 下面的配置项在当前代码示例中被注释掉，但可用于扩展
        "admin_email": app_configs.admin_email,
        "items_per_user": app_configs.items_per_user,
        # "database_url_dev": app_configs.database_url_dev,  # 示例，实际应用中可能需要根据环境变量动态获取
        "db_url": db_configs.get_database_url("dev"),
    }


@app.get("/test/")
def create_chat_history_table():
    table_name = "chat_history_lc"
    PostgresChatMessageHistory.create_tables(DbEngine.get_psycopg_conn(), table_name)

    # Initialize the chat history manager
    chat_history = PostgresChatMessageHistory(
        table_name,
        "5cc22949-e0f2-40c3-ac0a-889315a195a0",
        sync_connection=DbEngine.get_psycopg_conn(),
    )
    # Add messages to the chat history
    chat_history.add_messages(
        [
            SystemMessage(content="Meow"),
            AIMessage(content="woof"),
            HumanMessage(content="bark"),
        ]
    )

    return {"done"}


@app.get("/test2/")
def chat(
    chat_session_id: str,
    chat_input: str,
    session: Session = Depends(DbEngine.get_session),
):

    # 5b9d15f2-d163-42cb-9570-f1b985ff9995

    async def generate():
        for chunk in chatWithHistory(
            chat_session_id=chat_session_id, chat_input=chat_input, session=session
        ):
            yield chunk.content.encode()  # 将内容转为字节，因为StreamingResponse需要字节流

    headers = {
        "Content-Type": "text/plain",
    }
    return StreamingResponse(generate(), headers=headers, media_type="text/plain")
    # return chatWithHistory(
    #     chat_session_id=chat_session_id, chat_input=chat_input, session=session
    # )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
