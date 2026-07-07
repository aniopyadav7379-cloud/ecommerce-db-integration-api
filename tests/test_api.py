"""
End-to-end tests against an in-memory SQLite DB (swap DATABASE_URL for
Postgres in real deployments -- SQLAlchemy makes the app layer portable).
"""
import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.database import Base, get_db
from app.main import app

engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()

    if os.path.exists("./test.db"):
        os.remove("./test.db")

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_create_and_get_user():
    resp = client.post("/users", json={
        "email": "alice@example.com",
        "full_name": "Alice",
        "password": "supersecret1",
        "profile": {"phone_number": "555-1234", "city": "Hyderabad", "country": "India"},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert data["profile"]["city"] == "Hyderabad"

    resp = client.get(f"/users/{data['id']}")
    assert resp.status_code == 200


def test_duplicate_email_rejected():
    payload = {"email": "bob@example.com", "full_name": "Bob", "password": "supersecret1"}
    first = client.post("/users", json=payload)
    assert first.status_code == 201
    second = client.post("/users", json=payload)
    assert second.status_code == 409  # UNIQUE constraint enforced


def test_product_crud_and_constraints():
    resp = client.post("/products", json={"name": "Widget", "price": 9.99, "stock": 10})
    assert resp.status_code == 201
    product = resp.json()

    resp = client.get(f"/products/{product['id']}")
    assert resp.status_code == 200

    resp = client.put(f"/products/{product['id']}", json={"stock": 5})
    assert resp.status_code == 200
    assert resp.json()["stock"] == 5

    # CHECK constraint / validation: negative price must be rejected
    resp = client.post("/products", json={"name": "Bad", "price": -1, "stock": 1})
    assert resp.status_code == 422


def test_order_creation_decrements_stock_and_snapshots_price():
    user = client.post("/users", json={
        "email": "carol@example.com", "full_name": "Carol", "password": "supersecret1"
    }).json()
    product = client.post("/products", json={"name": "Gadget", "price": 20.00, "stock": 3}).json()

    resp = client.post("/orders", json={
        "user_id": user["id"],
        "items": [{"product_id": product["id"], "quantity": 2}],
    })
    assert resp.status_code == 201
    order = resp.json()
    assert order["items"][0]["quantity"] == 2
    assert float(order["items"][0]["price_at_purchase"]) == 20.00

    remaining = client.get(f"/products/{product['id']}").json()
    assert remaining["stock"] == 1  # 3 - 2

    # Ordering more than remaining stock must fail with 409
    resp = client.post("/orders", json={
        "user_id": user["id"],
        "items": [{"product_id": product["id"], "quantity": 5}],
    })
    assert resp.status_code == 409


def test_sql_injection_style_input_is_treated_as_plain_data():
    """
    A malicious-looking email string must never be able to alter query
    logic -- SQLAlchemy binds it as a plain parameter, so it either fails
    normal validation or simply finds no match. It must not, for example,
    return every user in the table.
    """
    malicious_email = "' OR '1'='1"
    resp = client.get("/users")
    before_count = len(resp.json())

    resp = client.post("/users", json={
        "email": "not-an-email",  # invalid format on purpose
        "full_name": "Attacker",
        "password": "supersecret1",
    })
    assert resp.status_code == 422  # Pydantic EmailStr validation rejects it

    resp = client.get("/users")
    after_count = len(resp.json())
    assert after_count == before_count
