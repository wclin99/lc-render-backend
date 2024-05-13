from functools import lru_cache
import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated, Union, Optional
from fastapi import FastAPI,Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from .db import create_db_and_tables, DbEngine,Todo
from .config import AppConfigs, DatabaseConfigs, app_configs, db_configs


def get_engine():
    return DbEngine.get_instance()

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
    create_db_and_tables(get_engine())
    yield



app = FastAPI(lifespan=lifespan)


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
    return {"message": "backend connected"}


# 使用 lru_cache 装饰器缓存 get_configs 函数的返回结果
# 函数用于获取配置信息
@lru_cache
def get_configs():
    """
    获取配置对象的实例。

    Returns:
        Configs: 配置信息的实例。
    """
    return AppConfigs()


@app.get("/info")
async def info(settings: Annotated[AppConfigs, Depends(get_configs)]):
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


# 读取所有待办事项
@app.get("/todos/")
def read_todos():
    """
    从数据库中读取所有待办事项。

    返回:
    - 所有待办事项的列表。
    """
    with Session(get_engine()) as session:
        # 执行SQL查询所有待办事项，并获取结果
        todos = session.exec(select(Todo)).all()
        # 返回所有待办事项的列表
        return todos



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
