from pathlib import Path
import shutil

import pytest
from fastapi.testclient import TestClient

import app.config as config
import app.excel_handler as excel
from app.main import app


@pytest.fixture(autouse=True)
def isolated_workbook(tmp_path, monkeypatch):
    workbook = tmp_path / "library_data.xlsx"
    monkeypatch.setattr(config, "WORKBOOK_PATH", workbook)
    monkeypatch.setattr(excel, "WORKBOOK_PATH", workbook)
    excel.initialize_workbook()
    yield
    if workbook.exists():
        workbook.unlink()


@pytest.fixture
def client():
    return TestClient(app)


def login(client, username, password):
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def librarian_headers(client):
    token = login(client, "admin", "admin123")
    return {"Authorization": f"Bearer {token}"}


def test_login_and_role_access(client):
    headers = librarian_headers(client)
    response = client.get("/members", headers=headers)
    assert response.status_code == 200
    member_token = login(client, "member", "member123")
    member_headers = {"Authorization": f"Bearer {member_token}"}
    assert client.get("/members", headers=member_headers).status_code == 403


def test_registration_approval_and_borrow_workflow(client):
    registration = client.post("/auth/register", json={
        "FName": "Alex",
        "LName": "Reader",
        "phone": "1234567890",
        "email": "alex@example.com",
        "address": "Library Road",
        "username": "alex",
        "password": "reader123",
    })
    assert registration.status_code == 201
    rid = registration.json()["RID"]

    headers = librarian_headers(client)
    approved = client.patch(f"/auth/registrations/{rid}/approve", headers=headers)
    assert approved.status_code == 200
    mid = approved.json()["MID"]

    token = login(client, "alex", "reader123")
    member_headers = {"Authorization": f"Bearer {token}"}
    request = client.post("/borrow/request", json={"bid": "B001"}, headers=member_headers)
    assert request.status_code == 201
    tid = request.json()["TID"]

    approval = client.patch(f"/borrow/{tid}/approve", headers=headers)
    assert approval.status_code == 200
    book = client.get("/books/B001", headers=headers).json()
    assert book["AvailableCopies"] == 4

    returned = client.post(f"/borrow/{tid}/return", json={"return_date": "2026-11-20"}, headers=headers)
    assert returned.status_code == 200
    book = client.get("/books/B001", headers=headers).json()
    assert book["AvailableCopies"] == 5
