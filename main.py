import re
import os
import bs4
import time
from langchain import hub
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from langchain_postgres.vectorstores import PGVector

from functools import lru_cache
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from sqlmodel import Session, distinct, select
import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated, List, Union, Optional
from fastapi import FastAPI, Depends, Query, Request, Body, status, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from lib.chat.chat_history import ChatHistory
from lib.db import DbEngine, Todo
from lib.config import app_configs, db_configs, api_configs
from langchain_postgres import PostgresChatMessageHistory
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from lib.db import User_chat_session
from lib.model import ResponseModel, ApiDocTags, ChatRole, Environments
from routers import router_chat_history, router_chat_session, router_demo
from fastapi.testclient import TestClient
from lib.chat.chat import chatWithAnyDocument, chatWithDocument, chatWithHistory
from fastapi.responses import StreamingResponse
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from lib.chat import model
from langchain_text_splitters import RecursiveCharacterTextSplitter


useEnv = Environments.main


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
    DbEngine.init_db(conn_str=db_configs.get_database_url(useEnv))
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
    return {
        "repo branch": "development",
        "database branch": useEnv,
        "session_id": DbEngine.get_session_id(),
    }


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
        "db_branch": useEnv,
        "db_conn_str": db_configs.get_database_url(useEnv),
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


@app.get("/test_chat_with_history/")
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


# @app.get("/test3/")
# def test_web_loader():
#     # Load, chunk and index the contents of the blog.
#     loader = WebBaseLoader(
#         web_paths=("https://lilianweng.github.io/posts/2023-06-23-agent/",),
#         bs_kwargs=dict(
#             parse_only=bs4.SoupStrainer(
#                 class_=("post-content", "post-title", "post-header")
#             )
#         ),
#     )
#     docs = loader.load()
#     text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
#     splits = text_splitter.split_documents(docs)
#     # vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
#     pc = Pinecone(api_key=api_configs.pinecone_api_key)
#     index_name = "ux-prototype"
#     existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
#     if index_name not in existing_indexes:
#         pc.create_index(
#             index_name,
#             dimension=1536,
#             metric="cosine",
#             spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#         )
#         while not pc.describe_index(index_name).status["ready"]:
#             time.sleep(1)
#     index = pc.Index(index_name)
#     vectorstore = PineconeVectorStore.from_documents(
#         documents=docs, embedding=OpenAIEmbeddings(), index_name=index_name
#     )

#     # Retrieve and generate using the relevant snippets of the blog.
#     retriever = vectorstore.as_retriever()
#     prompt = hub.pull("rlm/rag-prompt")
#     # You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
#     # Question: {question}
#     # Context: {context}
#     # Answer:
#     llm = model
#     rag_chain = (
#         {"context": retriever | format_docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )

#     return rag_chain.invoke("What is Task Decomposition?")


# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)


# @app.get("/test4/")
# def test_web_loader2():
#     markdown_document = "# 产品介绍\n\n欢迎踏入奇思妙想的世界，探索**奇迹向量5000**——一项技术幻想的飞跃，承诺在绝对无用的同时，以它奇幻的功能让你目眩神迷。无论你是技术狂热者还是寻觅乐趣的旅人，**奇迹向量5000**定会让你在惊喜与困惑中找到平衡。让我们一起揭开这款现代胡言乱语奇迹的虚构规格、设置流程以及故障排除小贴士的神秘面纱。\n\n## 产品概览\n\n**奇迹向量5000**满载着超越逻辑与物理的特性，每一项设计都旨在听起来令人印象深刻，同时保持一抹荒诞不经的趣味：\n\n- **超量子跃迁引擎**：作为**奇迹向量5000**的核心，此引擎基于超量子跃迁原理运作，一种既神秘又无意义的现象。它利用不可能性力量，在多维空间内无缝运行。\n\n- **超立方体潜能矩阵**：这一组件将无限可能压缩至单一超立方体状态，使设备能够以0%的准确率预测结果，确保每次使用都是全新的探险。\n\n- **以太波动电容器**：从虚构的以太中汲取能量，该电容器通过挖掘无限想象能量场的无尽储备，提供源源不断的动力。\n\n- **多维度全息界面**：通过其全息界面与**奇迹向量5000**互动，该界面在三加半维度上投射控制和信息，创造一个既未来感十足又令人费解的用户体验。\n\n- **神经狂欢同步器**：这项先进功能直接连接用户的脑波，将你最深邃的想法转化为可触摸的行动——尽管结果总是充满奇趣且难以预料。\n\n- **时空扭曲场**：利用**奇迹向量5000**的时空扭曲场操控时间本身，让你可以体验即将发生或重新经历处于时间流动中的瞬间。\n\n## 应用场景\n\n尽管**奇迹向量5000**本质上是一个虚构的乐趣装置，让我们想象一些它理论上可以应用的场景：\n\n- **时空旅行冒险**：利用时空扭曲场访问历史的关键时刻或窥探未来。虽然实际的时间操控不可能，但这一想法本身就激发了无限的叙事可能。\n\n- **跨维度游戏体验**：通过多维度全息界面沉浸于超脱现实的游戏体验中。想象一下，游戏通过神经狂欢同步器与你的思想相连，创造出独一无二、不断变化的环境。\n\n- **无限创意激发**：利用超立方体潜能矩阵进行头脑风暴会议。通过将无限可能压缩至超立方体状态，理论上能帮助解锁前所未有的创意想法。\n\n- **能源探索**：探索从以太中提取无限能量的概念。虽然纯属虚构，但从以太中汲取能量的设想或许能启发能源研究的新思维。\n\n## 上手指南\n\n启动你的**奇迹向量5000**既简单又荒谬地复杂。遵循以下步骤释放新设备的全部潜能：\n\n1. **开箱设备**：从反重力包装中取出**奇迹向量5000**，注意轻拿轻放，以免干扰其组件的微妙平衡。\n\n2. **启动超量子跃迁引擎**：找到标有“QFE启动”的透明杆并轻轻拉动。你应该能看到空气中有轻微的闪烁，表明超量子跃迁正在生效。\n\n3. **校准超立方体潜能矩阵**：转动标有“无限A”和“无限B”的旋钮，直至矩阵稳定。当显示屏显示一个稳定的“∞”时，说明已校准正确。\n\n## 故障排查\n\n即便是设计得如此奇妙的**奇迹向量5000**也可能遇到问题。这里有一些常见问题及其解决方案：\n\n- **问题**：超量子跃迁引擎无法启动。\n    - **解决方案**：确保反重力包装已完全移除，并检查是否有任何不可能性碎片阻碍了引擎。"
#     headers_to_split_on = [("#", "Header 1"), ("##", "Header 2")]

#     markdown_splitter = MarkdownHeaderTextSplitter(
#         headers_to_split_on=headers_to_split_on, strip_headers=False
#     )
#     md_header_splits = markdown_splitter.split_text(markdown_document)

#     embeddings = DashScopeEmbeddings(
#         model="text-embedding-v2", dashscope_api_key=api_configs.dashscope_api_key
#     )
#     pc = Pinecone(api_key=api_configs.pinecone_api_key)
#     index_name = "ux-prototype"
#     existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]
#     if index_name not in existing_indexes:
#         pc.create_index(
#             index_name,
#             dimension=1536,
#             metric="cosine",
#             spec=ServerlessSpec(cloud="aws", region="us-east-1"),
#         )
#         while not pc.describe_index(index_name).status["ready"]:
#             time.sleep(1)
#     index = pc.Index(index_name)
#     namespace = "wondervector5000-zh"

#     docsearch = PineconeVectorStore.from_documents(
#         documents=md_header_splits,
#         index_name=index_name,
#         embedding=embeddings,
#         namespace=namespace,
#     )

#     collection_name = namespace

#     vectorstore = PGVector.from_documents(
#         embedding=embeddings,
#         documents=md_header_splits,
#         connection=db_configs.get_database_url(useEnv),
#         collection_name=collection_name,
#         use_jsonb=True,
#     )

#     time.sleep(1)

#     for ids in index.list(namespace=namespace):
#         query = index.query(
#             id=ids[0],
#             namespace=namespace,
#             top_k=1,
#             include_values=True,
#             include_metadata=True,
#         )
#         print(query)

#     llm = model

#     # retriever = docsearch.as_retriever()
#     retriever = vectorstore.as_retriever()

#     prompt = hub.pull("rlm/rag-prompt")

#     rag_chain = (
#         {"context": retriever | format_docs, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | StrOutputParser()
#     )
#     query1 = "启动奇迹向量5000的前三个步骤是什么？"
#     return rag_chain.invoke(query1)


@app.post("/test5/")
def chat_with_doc(file: UploadFile,namespace: str,query:str):
    return chatWithAnyDocument(file,
                            namespace,
                            db_configs.get_database_url(useEnv),
                            query)


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    file_name = file.filename

    file_extension = os.path.splitext(file_name)[1].lower()

    return {"ext": file_extension}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
