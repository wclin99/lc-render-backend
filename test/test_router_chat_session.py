import pytest
from fastapi.testclient import TestClient
from main import app  # 假设您的 FastAPI 应用实例在 main.py 中

from lib.model import ChatRole


client = TestClient(app)


class TestChatHistory:
    """
    测试聊天历史记录的类。
    包含对聊天历史记录的发布和获取功能的测试方法。
    """

    @pytest.mark.parametrize(
        "chat_session, role, content",
        [
            ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.system, "Posted by pytest..."),
            ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.ai, "Posted by pytest..."),
            ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.human, "Posted by pytest..."),
        ],
    )
    def test_post_chat_history(self, chat_session, role, content):
        """
        测试发布聊天历史记录的功能。

        参数:
        - chat_session: 聊天会话的唯一标识符。
        - role: 发布聊天内容的角色（系统、AI或人类）。
        - content: 要发布的聊天内容。

        返回值:
        - 无返回值，但断言测试是否成功。
        """
        response = client.post(
            "/chat_history/post/",
            json={  # 发送POST请求发布聊天历史记录
                "chat_session": chat_session,
                "role": role,
                "content": content
            }
        )
        assert response.status_code == 200  # 断言响应状态码为200
        data = response.json()  # 将响应内容解析为JSON
        assert data["success"] is True  # 断言操作成功
        assert "data" in data  # 断言响应数据包含"数据"字段


    def test_get_chat_history(self):
        """
        测试获取聊天历史记录的功能。

        参数:
        - 无参数。

        返回值:
        - 无返回值，但断言测试是否成功。
        """
        chat_session = "5cc22949-e0f2-40c3-ac0a-889315a195a0"  # 指定要获取聊天历史记录的聊天会话标识符
        response = client.get(
            "/chat_history/get/",
            params={"chat_session": chat_session}  # 通过GET请求参数指定聊天会话标识符
        )
        assert response.status_code == 200  # 断言响应状态码为200
        data = response.json()  # 将响应内容解析为JSON
        assert data["success"] is True  # 断言操作成功
        assert "data" in data  # 断言响应数据包含"数据"字段