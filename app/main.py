from fastapi import FastAPI

from app.api.routes import users, products, orders

app = FastAPI(
    title="E-Commerce Database Integration API",
    description=(
        "Project 3 - Database Integration (DecodeLabs Full Stack Development). "
        "Demonstrates schema design, CRUD operations, RESTful mapping, "
        "and protection against SQL injection via parameterized ORM queries."
    ),
    version="1.0.0",
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)


@app.get("/health", tags=["health"])
def health_check():
    """Simple liveness check -- does not touch the database."""
    return {"status": "ok"}
