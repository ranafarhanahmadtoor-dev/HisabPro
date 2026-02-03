from fastapi import FastAPI
from .database import engine, Base
from .routers import auth, sales, inventory, payment, reports, frontend
import asyncio

app = FastAPI(title="HisabPro", version="1.0.0")

# Create tables on startup (for dev simplicity)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth.router)
app.include_router(payment.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(reports.router)
app.include_router(frontend.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to HisabPro API"}
