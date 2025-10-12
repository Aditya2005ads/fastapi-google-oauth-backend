from fastapi import FastAPI
from contextlib import asynccontextmanager
from App.database import init_db
from App.routers import auth
from App.routers import restaurants, payments, orders, analytics


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")
    init_db()
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(restaurants.router)
app.include_router(payments.router)
app.include_router(orders.router)
app.include_router(analytics.router)

@app.get("/")
def index():
    return {"msg": "Hello World"}

@app.get("/health")
def health_check(): 
    return {"status": "ok"}


