# E-Commerce Database Integration API
**DecodeLabs Full Stack Development — Industrial Training Kit, Project 3**

FastAPI + PostgreSQL backend implementing the four pillars from the project brief:

| Pillar | What it covers | Where |
|---|---|---|
| 1. The Blueprint (Schema & Design) | Tables, relationships, keys | `app/models/`, `alembic/versions/0001_initial_schema.py` |
| 2. The Bridge (Integration) | ORM connecting code to Postgres | `app/db/database.py` (SQLAlchemy) |
| 3. The Action (CRUD & REST) | Create/Read/Update/Delete mapped to POST/GET/PUT/DELETE | `app/crud/`, `app/api/routes/` |
| 4. The Shield (Integrity & Security) | Constraints + parameterized queries | Model `CheckConstraint`/`unique=True`, SQLAlchemy ORM (no string concatenation anywhere) |

## Schema design (the three relationship types from the brief)

- **One-to-One**: `User` ↔ `UserProfile` (enforced by `unique=True` on `user_profiles.user_id`)
- **One-to-Many**: `User` → `Order` (a user places many orders)
- **Many-to-Many**: `Product` ↔ `Order`, through the `OrderItem` junction table, which also stores `quantity` and `price_at_purchase` so historical orders never change if a product's price changes later

Constraints enforced at the database level (not just in application code):
- `UNIQUE` on `users.email` and `user_profiles.user_id`
- `NOT NULL` on all required fields
- `CHECK` constraints: `price >= 0`, `stock >= 0`, `quantity > 0`

## Security: SQL injection

Every query goes through SQLAlchemy's ORM (`db.get(...)`, `select(...).where(...)`), which always binds parameters instead of concatenating strings. There is no raw SQL string-building anywhere in this codebase. `test_sql_injection_style_input_is_treated_as_plain_data` in the test suite demonstrates this directly.

## Project layout

```
ecommerce-db-project/
├── app/
│   ├── core/config.py        # env-based settings
│   ├── db/database.py        # engine, session, Base
│   ├── db/base.py            # imports all models for Alembic
│   ├── models/                # User, UserProfile, Product, Order, OrderItem
│   ├── schemas/                # Pydantic request/response contracts
│   ├── crud/                  # Create/Read/Update/Delete logic per entity
│   ├── api/routes/            # REST endpoints
│   └── main.py                # FastAPI app
├── alembic/                   # DB migrations (versioned schema history)
├── tests/test_api.py          # CRUD + constraint + injection tests
├── docker-compose.yml         # Postgres + API, one command to run both
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Running it

### Option A — Docker (recommended, matches production setup)
```bash
cp .env.example .env
# edit .env with a real password
docker compose up --build
```
API will be live at `http://localhost:8000`, interactive docs at `http://localhost:8000/docs`.

### Option B — Local Python + local Postgres
```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point DATABASE_URL at your local Postgres
alembic upgrade head
uvicorn app.main:app --reload
```

## Running the tests
Tests run against an in-memory-style SQLite file so no live Postgres is required to verify logic:
```bash
pip install -r requirements.txt
python -m pytest tests/ -v
```
All 6 tests currently pass, covering: user creation + profile (1:1), duplicate-email rejection (UNIQUE), product CRUD + CHECK constraint validation, order creation with stock decrement and price snapshotting (M:M via junction table), insufficient-stock rejection, and injection-safety of query parameters.

## REST API reference

| Method | Path | Maps to |
|---|---|---|
| POST | `/users` | INSERT |
| GET | `/users`, `/users/{id}` | SELECT |
| PUT | `/users/{id}` | UPDATE |
| DELETE | `/users/{id}` | DELETE |
| POST | `/products` | INSERT |
| GET | `/products`, `/products/{id}` | SELECT |
| PUT | `/products/{id}` | UPDATE |
| DELETE | `/products/{id}` | DELETE |
| POST | `/orders` | INSERT (order + order_items, decrements stock) |
| GET | `/orders/{id}`, `/orders/user/{user_id}` | SELECT |
| PUT | `/orders/{id}/status` | UPDATE |
| DELETE | `/orders/{id}` | DELETE (restores stock) |

## Notes / next steps if extending this
- Add JWT auth (the brief's "complex user authentication" is explicitly the *next* milestone, not this one)
- Add pagination cursors instead of offset/limit for large tables
- Swap `Numeric` for a dedicated money type if adding multi-currency support
