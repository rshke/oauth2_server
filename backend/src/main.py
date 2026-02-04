from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.database import engine, Base, SessionLocal
from src.routes import router
import uvicorn
import logging
import traceback

# Configure basic logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        logger.info("Starting up...")
        # Create tables on startup for demo
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        # Seed data
        async with SessionLocal() as session:
            from sqlalchemy import select
            from src.models import Client, User
            
            # Seed Client
            result = await session.execute(select(Client).where(Client.client_id == "frontend_client"))
            client = result.scalar_one_or_none()
            if not client:
                client = Client(
                    client_id="frontend_client",
                    client_secret="secret",
                    grant_types="authorization_code",
                    response_types="code",
                    scope="read",
                    redirect_uris="http://localhost:5173/callback"
                )
                session.add(client)
                
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
app.include_router(router)

@app.get("/")
def home():
    return {"message": "OAuth2 Server is running"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
