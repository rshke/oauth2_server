from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database import engine, Base, SessionLocal
from src.routes import router
import uvicorn
import logging
import traceback
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up...")
        # Create tables on startup for demo
        # async with engine.begin() as conn:
        #     await conn.run_sync(Base.metadata.create_all)

        logger.info("Startup complete.")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        logger.error(traceback.format_exc())
        # Re-raise so the app fails to start if DB is bad
        raise e

    yield
    # Shutdown logic if any can go here


app = FastAPI(
    title="OAuth2 Provider",
    description="A simple OAuth2 provider implementation",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS to allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Session Middleware for Auth Session
app.add_middleware(SessionMiddleware, secret_key="super_secret_key")

app.include_router(router)


@app.get("/")
def home():
    return {"message": "OAuth2 Server is running"}


if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
