from datetime import datetime
import logging
import os
import tempfile
import time
from typing import Type
from fastapi import UploadFile
from langchain_postgres import PGVector
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain_core.documents import Document
import oss2
from oss2.credentials import EnvironmentVariableCredentialsProvider

from sqlmodel import Session
from langchain_community.embeddings import DashScopeEmbeddings
from langchain import hub
from lib.model import ChatRole
from langchain_core.output_parsers import StrOutputParser
from lib.config import api_configs

from .chat_model import model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from .chat_history import ChatHistory
from lib.config import logger_config
from langchain_community.document_loaders import (
    # WebBaseLoader,
    TextLoader,
    # ArxivLoader,
    # AirtableLoader,
    # BiliBiliLoader,
    # DropboxLoader,
    # FigmaFileLoader,
    # GoogleDriveLoader,
    # ObsidianLoader,
    PyPDFLoader,
    UnstructuredExcelLoader,
    UnstructuredMarkdownLoader,
    UnstructuredPowerPointLoader,
    UnstructuredWordDocumentLoader,
    # YuqueLoader,
)
from langchain_community.document_loaders.base import BaseLoader


def chatWithHistory(*, chat_session_id: str, chat_input: str, session: Session):

    message_history = []

    if not ChatHistory.get_sliced_messages():
        print("get_sliced_messages---empty!!!")
        ChatHistory.get_chat_messages_from_db(
            chat_session_id=chat_session_id, session=session
        )

    print("get_sliced_messages---not empty~~")
    for msg in ChatHistory.get_sliced_messages():
        if msg.role == ChatRole.human:
            message_history.append(HumanMessage(content=msg.content))
        elif msg.role == ChatRole.ai:
            message_history.append(AIMessage(content=msg.content))
        else:
            message_history.append(SystemMessage(content=msg.content))

    message_history.append((ChatRole.human, "{question}"))

    ChatHistory.add_message_to_instance_storage(role=ChatRole.human, content=chat_input)

    ChatHistory.add_chat_messages_to_db(
        [HumanMessage(content=chat_input)],
        session=session,
        chat_session_id=chat_session_id,
    )

    prompt = ChatPromptTemplate.from_messages(message_history)

    chain = prompt | model

    return chain.stream(
        {"question": {chat_input}},
    )

    # ----------- INVOKE版本-----------
    #
    # ai_message= chain.invoke(
    #     {"question": {chat_input}},
    # )

    # ChatHistory.push_message(role=ChatRole.ai, content=ai_message.content)
    # ChatHistory.add_chat_messages(
    #     [AIMessage(content=ai_message.content)],
    #     session=session,
    #     chat_session_id=chat_session_id,
    # )

    # return  {"message":ai_message.content,
    #          "history":{"len":message_history.__len__(),
    #                     "data":message_history}}
    #
    #  ----------- INVOKE版本-----------


def chatWithDocument(
    upload_file: UploadFile, namespace: str, db_connection_string: str, query: str
):

    doc_contents, doc_splitter = __splitDocument(upload_file)

    doc_splits = doc_splitter.split_text(doc_contents)

    # 载入embedding模型
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v2", dashscope_api_key=api_configs.dashscope_api_key
    )

    #  为文档生成主题词
    collection_name = namespace + datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 向量存储
    vectorstore = PGVector.from_documents(
        embedding=embeddings,
        documents=doc_splits,
        connection=db_connection_string,
        collection_name=collection_name,
        use_jsonb=True,
    )

    time.sleep(1)

    # 载入chat model
    llm = model

    # 创建retriever
    retriever = vectorstore.as_retriever()

    # 载入prompt
    prompt = hub.pull("rlm/rag-prompt")

    rag_chain = (
        {"context": retriever | __format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain.invoke(query)


def chatWithAnyDocument(
    upload_file: UploadFile, namespace: str, db_connection_string: str, query: str
):
    #  为文档生成主题词
    collection_name = namespace + "-" + datetime.now().strftime("%Y%m%d%H%M%S")
    logger_config.get_logger().info(f"Collection name: {collection_name}")


    file_name: str = upload_file.filename
    file_extension: str = os.path.splitext(file_name)[1].lower()

    auth = oss2.ProviderAuth(EnvironmentVariableCredentialsProvider())
    bucket = oss2.Bucket(
        auth, api_configs.oss_region_endpoint, api_configs.oss_bucket_name
    )

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        temp_file.write(upload_file.file.read())
        temp_file_path = temp_file.name



    oss_saved_path=str("rag/"+collection_name+file_extension)
    # 必须以二进制的方式打开文件。
    with open(temp_file_path, "rb") as fileobj:
        # 填写Object完整路径。Object完整路径中不能包含Bucket名称。
        bucket.put_object(oss_saved_path, fileobj)

    logger_config.get_logger().info(f"File uploaded and saved in oss: {oss_saved_path}")


    # 使用临时文件路径初始化 PyPDFLoader
    loader: BaseLoader = __create_loader(file_extension, temp_file_path)

    logger_config.get_logger().info("Loader created, loading documents...")

    # docs = loader.load_and_split()
    docs = loader.load()

    logger_config.get_logger().info("Documents loaded.")

    
    # 载入embedding模型
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v2", dashscope_api_key=api_configs.dashscope_api_key
    )

    logger_config.get_logger().info("Embeddings model loaded.")


    logger_config.get_logger().info("Storing embedded documents to vectorstore...")

    # 生成嵌入+向量存储
    vectorstore = PGVector.from_documents(
        embedding=embeddings,
        documents=docs,
        connection=db_connection_string,
        collection_name=collection_name,
        use_jsonb=True,
    )

    logger_config.get_logger().info("Documents stored in vectorstore.")

    time.sleep(1)
   


    # 载入chat model
    llm = model

    logger_config.get_logger().info("Chat model loaded.")

    # 创建retriever
    retriever = vectorstore.as_retriever()

    logger_config.get_logger().info("Retriever created.")

    # 载入prompt
    prompt = hub.pull("rlm/rag-prompt")
    # prompt要改

    logger_config.get_logger().info("Prompt loaded.")

    rag_chain = (
        {"context": retriever | __format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    logger_config.get_logger().info("RAG chain created, invoking query...")

    result = rag_chain.invoke(query)

    logger_config.get_logger().info("Query invoked, returning result.")

    os.remove(temp_file_path)

    return result


def __splitDocument(upload_file: UploadFile):
    file_name = upload_file.filename
    file_extension = os.path.splitext(file_name)[1].lower()
    if file_extension == ".md":
        doc_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[
                ("#", "Header 1"),
                ("##", "Header 2"),
                ("###", "Header 3"),
            ],
            strip_headers=False,
        )

    elif file_extension in [".txt", ".text"]:
        doc_splitter = RecursiveCharacterTextSplitter(
            separators=[
                "\n\n",  # 双换行分段
                "\n",  # 单换行
                " ",  # 空格
                ".",  # 英文句点
                ",",  # 英文逗号
                "\u200b",  # 零宽空格
                "\uff0c",  # 全角逗号
                "\u3001",  # 中文顿号
                "\uff0e",  # 全角句点
                "\u3002",  #  中文句号
                "?",  # 英文问号
                "\uff1f",  # 全角问号
                "!",  # 英文感叹号
                "\uff01",  # 全角感叹号
                # "\uff08",  # 全角左圆括号
                # "\uff09",  # 全角右圆括号
                # "\u300a",  # 全角左双引号
                # "\u300b",  # 全角右双引号
                # "\uff1a",  # 全角冒号
                "\uff1b",  # 全角分号
                # "-",      # 减号/连字符
                # "\u2212",  # 算术减号
                "\u2026",  # 水平省略号
                # "/",      # 斜线
                "\uff0d",  # 全角破折号
                # "\uff5e",  # 全角波浪线
                # "\ufe4f",  # 双波浪线
                "\u2014",  # 破折号
                "\u2013",  # 短破折号
                # "\u201c",  # 左双引号
                # "\u201d",  # 右双引号
            ],
        )
    else:
        raise ValueError(f"Unsupported file extension: {file_extension}")

    doc_content = upload_file.file.read().decode("utf-8")

    return doc_content, doc_splitter


def __format_docs(docs: list[Document]):
    return "\n\n".join(doc.page_content for doc in docs)


def __create_loader(ext, file_path) -> Type[BaseLoader]:
    loader_mapping = {
        ".txt": lambda path: TextLoader(path, autodetect_encoding=True),
        # txt 测试通过：readme文件
        ".md": lambda path: UnstructuredMarkdownLoader(path, mode="elements"),
        # md 测试通过：md格式论文
        # ".doc":lambda path: UnstructuredWordDocumentLoader(path),
        # doc 未测试
        ".docx": lambda path: UnstructuredWordDocumentLoader(path),
        # docx 测试通过：驾驶舱开发需求
        # ".xls":lambda path: UnstructuredExcelLoader(path, mode="elements"),
        # xls 未测试
        ".xlsx": lambda path: UnstructuredExcelLoader(path, mode="elements"),
        # xlsx 测试通过：小论文实验数据
        # ".ppt":lambda path: UnstructuredPowerPointLoader(path),
        # ppt 格式不行 -- 需要 libreOffice
        ".pptx": lambda path: UnstructuredPowerPointLoader(path),
        # pptx 测试通过：艾德莱斯绸介绍
        ".pdf": lambda path: PyPDFLoader(path),
        # pdf 测试通过：脑电设备说明书
        # ... 其他文件类型的处理逻辑
    }

    loader_creator = loader_mapping.get(ext, None)
    if loader_creator:
        return loader_creator(file_path)
    else:
        raise ValueError(f"No loader found for file extension '{ext}'")
