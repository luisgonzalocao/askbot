from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app

client = TestClient(app=app)


def test_ask_question():
    mock_rag = AsyncMock()
    mock_rag.ainvoke.return_value = "Mocked response"
    with patch.object(app, 'state', MagicMock(rag_chain=mock_rag)):
        test_question = {"question": "What services does Promtior offer?"}
        response = client.post("/ask", json=test_question)
        assert response.status_code == 200
        assert response.json()["answer"] == "Mocked response"


def test_ask_question_without_rag():
    with patch.object(app, 'state', MagicMock(rag_chain=None)):
        test_question = {"question": "What's Promtior?"}
        response = client.post("/ask", json=test_question)
        assert response.status_code == 503
        assert "initializing" in response.json()["detail"].lower()


def test_ask_question_with_model_failure():
    mock_rag = AsyncMock()
    mock_rag.ainvoke.side_effect = Exception("Model failed")
    with patch.object(app, 'state', MagicMock(rag_chain=mock_rag)):
        test_question = {"question": "What's Promtior?"}
        response = client.post("/ask", json=test_question)
        assert response.status_code == 500
        assert "failed" in response.json()["detail"].lower()


def test_serve_index():
    with patch("app.main.FileResponse", return_value="Mocked index.html") as mock_response:
        response = client.get("/")
        mock_response.assert_called_once_with("index.html")
        assert response.json() == "Mocked index.html"

