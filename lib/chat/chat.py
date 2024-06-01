from ast import List
from calendar import c
from typing import Sequence
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from sqlmodel import Session

from lib.model import ChatRole

from .chat_model import model
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, ConfigurableFieldSpec
from .chat_history import ChatHistory, SimpleMessage


def chatWithHistory(*, chat_session_id: str, chat_input: str, session: Session):

    message_history = []

    if not ChatHistory.get_sliced_messages():
        print("get_sliced_messages---empty!!!")
        ChatHistory.get_chat_messages(chat_session_id=chat_session_id, session=session)

    print("get_sliced_messages---not empty~~")
    for msg in ChatHistory.get_sliced_messages():
        if msg.role == ChatRole.human:
            message_history.append(HumanMessage(content=msg.content))
        elif msg.role == ChatRole.ai:
            message_history.append(AIMessage(content=msg.content))
        else:
            message_history.append(SystemMessage(content=msg.content))

    message_history.append((ChatRole.human, "{question}"))

    ChatHistory.push_message(role=ChatRole.human, content=chat_input)

    ChatHistory.add_chat_messages(
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
