"""FastAPI アプリケーションの API テスト。"""

import unittest

from fastapi.testclient import TestClient

from app import app


class AppApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_health(self) -> None:
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn(data["backend"], ("rule", "openai"))

    def test_chat_rule_based(self) -> None:
        response = self.client.post(
            "/api/chat",
            json={"message": "こんにちは"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("こんにちは", data["reply"])
        self.assertTrue(data["session_id"])
        self.assertEqual(len(data["messages"]), 2)

    def test_chat_continues_session(self) -> None:
        first = self.client.post("/api/chat", json={"message": "こんにちは"}).json()
        second = self.client.post(
            "/api/chat",
            json={"message": "ありがとう", "session_id": first["session_id"]},
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["session_id"], first["session_id"])
        self.assertEqual(len(second.json()["messages"]), 4)

    def test_get_history(self) -> None:
        chat = self.client.post("/api/chat", json={"message": "hello"}).json()
        response = self.client.get(f"/api/history/{chat['session_id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

    def test_delete_session(self) -> None:
        chat = self.client.post("/api/chat", json={"message": "hello"}).json()
        response = self.client.delete(f"/api/session/{chat['session_id']}")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["deleted"])

    def test_index_page(self) -> None:
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])


if __name__ == "__main__":
    unittest.main()
