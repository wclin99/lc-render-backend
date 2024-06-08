# import os
# import pytest
# from fastapi.testclient import TestClient
# from lib.db import DbEngine
# from main import app
# from lib.model import ChatRole, Environments
# from lib.config import db_configs
# from routers.router_chat_history import (
#     post_chat_history_to_db,
#     get_chat_history_from_db,
# )
# from sqlmodel import SQLModel, Session, create_engine

# def override_get_test_session():
#     db = create_engine(db_configs.get_database_url(Environments.test))
#     with Session(db) as session:
#         yield session

# app.dependency_overrides[DbEngine.get_session]=override_get_test_session

# client = TestClient(app)


# class TestChatHistory:

#     # def test_post(self):
#     #     response = client.post(
#     #         "/chat_history/post/",
#     #         json={
#     #             "chat_session": "5cc22949-e0f2-40c3-ac0a-889315a195a0",
#     #             "role": "system",
#     #             "content": "Some chat messages here...",
#     #         },
#     #     )
        
      
#     #     response_json = response.json()
#     #     assert response.is_success == True
#     #     assert response.status_code == 200

#         # @pytest.mark.parametrize(
#         #     "chat_session, role, content",
#         #     [
#         #         ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.system, "Posted by pytest..."),
#         #         ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.ai, "Posted by pytest..."),
#         #         ("5cc22949-e0f2-40c3-ac0a-889315a195a0", ChatRole.human, "Posted by pytest..."),
#         #     ],
#         # )
#         # def test_post_chat_history(self, chat_session, role, content):
#         #     response = client.post(
#         #         "/chat_history/post/",
#         #         json={
#         #             "chat_session": chat_session,
#         #             "role": role,
#         #             "content": content,
#         #         },
#         #     )
#         #     assert response.status_code == 200
#         #     assert response.json()["success"] is True

#         @pytest.mark.parametrize(
#             "chat_session",
#             ["5cc22949-e0f2-40c3-ac0a-889315a195a0", "another_test_session"],
#         )
#         def test_get_chat_history(self, chat_session):
#             response = client.get(f"/chat_history/get/?chat_session={chat_session}")
#             assert response.status_code == 200
#             assert response.json()["success"] is True
#             assert "messages" in response.json()["data"]
