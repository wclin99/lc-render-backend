
import os
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session
from main import app  # 假设您的 FastAPI 应用实例在 main.py 中
from lib.model import ChatRole,Environments 
from lib.config import db_configs


client = TestClient(app)


def test_read_env_var():
    test_url=db_configs.get_database_url(Environments.test)
    assert test_url == "postgresql://dev:Ab4w0gMRCLiH@ep-steep-butterfly-a14zk9q6.ap-southeast-1.aws.neon.tech/dev"
    # assert os.getenv("OPENAI_API_KEY") is not None