from fastapi.testclient import TestClient
import importlib
from pathlib import Path
import os

import main  # твоят файл с FastAPI приложението


def make_client(tmp_path, monkeypatch) -> TestClient:
    """
    Изолира сториджа в временна папка и ресетва броячите преди всеки тест.
    Връща TestClient за приложението.
    """
    # Насочваме STORAGE_DIR към временната директория
    monkeypatch.setattr(main, "STORAGE_DIR", tmp_path, raising=True)
    main.STORAGE_DIR.mkdir(exist_ok=True)

    # Ресетваме брояча спрямо текущото състояние на новата папка
    main.files_stored_counter = main.get_file_count()

    # Връщаме клиент
    return TestClient(main.app)


def test_root_lists_endpoints(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    r = client.get("/")
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "File Storage API"
    # Проверяваме, че основните endpoints присъстват
    for ep in ["GET /files/{filename}", "POST /files", "GET /files", "GET /health", "GET /metrics"]:
        assert ep in data["endpoints"]


def test_health_ok(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    r = client.get("/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "healthy"
    assert data["service"] == "File Storage API"
    assert "timestamp" in data


def test_list_empty_then_upload_and_list(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    # Първоначално е празно
    r = client.get("/files")
    assert r.status_code == 200
    assert r.json() == {"files": [], "count": 0}

    # Качваме файл
    content = b"hello world"
    r = client.post(
        "/files",
        files={"file": ("example.txt", content, "text/plain")},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "File stored successfully"
    assert data["filename"] == "example.txt"
    assert data["size"] == len(content)

    # Вече трябва да е наличен
    r = client.get("/files")
    assert r.status_code == 200
    data = r.json()
    assert "example.txt" in data["files"]
    assert data["count"] == 1


def test_download_existing_file(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    # Качваме файл
    payload = b"test-contents"
    client.post("/files", files={"file": ("note.txt", payload, "text/plain")})

    # Сваляме го
    r = client.get("/files/note.txt")
    assert r.status_code == 200
    assert r.content == payload
    # Проверка за тип (FileResponse с octet-stream)
    assert r.headers.get("content-type", "").startswith("application/octet-stream")


def test_download_missing_file_returns_404(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    r = client.get("/files/missing.txt")
    assert r.status_code == 404
    assert "not found" in r.json()["detail"].lower()


def test_path_traversal_blocked(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    r = client.get("/files/../secret.txt")
    assert r.status_code == 404  # route doesn't match -> 404



def test_metrics_before_and_after_upload(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    # Преди качване
    m1 = client.get("/metrics").json()
    assert m1["files_stored_total"] == 0
    assert m1["files_current"] == 0
    assert m1["total_storage_bytes"] == 0
    assert "timestamp" in m1

    # Качваме 1 файл
    data = b"a" * 10
    client.post("/files", files={"file": ("a.txt", data, "text/plain")})

    # След качване
    m2 = client.get("/metrics").json()
    assert m2["files_stored_total"] == 1
    assert m2["files_current"] == 1
    assert m2["total_storage_bytes"] == len(data)
    assert m2["total_storage_mb"] == round(len(data) / (1024 * 1024), 2)
