from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from lib.config import api_configs


# model = ChatOpenAI(model="gpt-3.5-turbo")
model = ChatTongyi(model="qwen-max", dashscope_api_key=api_configs.dashscope_api_key,streaming=True)
