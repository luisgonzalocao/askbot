from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "OK"


def test_ask_question():
    # Configura el estado de la app para la prueba
    mock_rag = AsyncMock()
    mock_rag.ainvoke.return_value = "Mocked response"

    # Usa MagicMock para simular el estado de la app
    with patch.object(app, 'state', MagicMock(rag_chain=mock_rag)):
        test_question = {"question": "What services does Promtior offer?"}
        response = client.post("/ask", json=test_question)

        assert response.status_code == 200
        assert response.json()["answer"] == "Mocked response"
