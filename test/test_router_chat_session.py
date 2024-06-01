import pytest
from fastapi.testclient import TestClient
from main import app  # 假设您的 FastAPI 应用实例在 main.py 中

from lib.model import ResponseModel, ChatRole





client = TestClient(app)


class TestChatHistory:

    @pytest.mark.parametrize(
        "chat_session, role, content",
        [
            ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.system, "Posted by pytest..."),
            ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.ai, "Posted by pytest..."),
            ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.human, "Posted by pytest..."),
        ],
    )
    def test_post_chat_history(self, chat_session, role, content):
        response = client.post(
            "/chat_history/post/",
            json={
                "chat_session": chat_session,
                "role": role,
                "content": content
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data

    def test_get_chat_history(self):
        chat_session = "5cc22949-e0f2-40c3-ac0a-889315a195a0"
        response = client.get(
            "/chat_history/get/",
            params={"chat_session": chat_session}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
