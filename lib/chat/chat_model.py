from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from lib.config import api_configs




# model = ChatOpenAI(model="gpt-3.5-turbo")

# NOTE: langchian 已经带有了一个合并的 Tongyi 实现, 
# 当时写这个项目的时候 Tongyi 的功能还不够完善, 不过随着后续的迭代应该已经没问题了
# 建议优先考虑通过以下方式使用
# from langchain_community.llms.tongyi import Tongyi
# from langchain_community.chat_models.tongyi import ChatTongyi

model = ChatTongyi(model="qwen-max", dashscope_api_key=api_configs.dashscope_api_key,streaming=True)