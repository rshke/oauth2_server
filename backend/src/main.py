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

        # Seed data
        async with SessionLocal() as session:
            from sqlalchemy import select
            from src.models import Client, User

            # Seed Client
            result = await session.execute(
                select(Client).where(Client.client_id == "frontend_client")
            )
            client = result.scalar_one_or_none()
            if not client:
                client = Client(
                    client_id="frontend_client",
                    client_secret="secret",
                    grant_types="authorization_code",
                    response_types="code",
                    scope="read",
                    redirect_uris="http://localhost:5173/callback",
                )
                session.add(client)

            # Seed Demo Client (for the separate Client App)
            result = await session.execute(
                select(Client).where(Client.client_id == "demo_client")
            )
            demo_client = result.scalar_one_or_none()
            if not demo_client:
                demo_client = Client(
                    client_id="demo_client",
                    client_secret="demo_secret",
                    grant_types="authorization_code",
                    response_types="code",
                    scope="read",
                    redirect_uris="http://localhost:3000/callback",
                )
                session.add(demo_client)

            # Seed User
            result = await session.execute(select(User).where(User.username == "demo"))
            user = result.scalar_one_or_none()
            if not user:
                user = User(username="demo", password_hash="demo")
                session.add(user)

            await session.commit()
        logger.info("Startup complete.")
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        logger.error(traceback.format_exc())
        # Re-raise so the app fails to start if DB is bad
        raise e

    yield
    # Shutdown logic if any can go here


app = FastAPI(lifespan=lifespan)

# Add CORS to allow Frontend to talk to Backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
    ],  # Frontend and Client
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
