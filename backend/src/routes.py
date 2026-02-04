from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.oauth import server
from src.database import get_db, SessionLocal
from src.models import User, Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aioauth.requests import Request as AioAuthRequest
from src.models import User as UserModel
from pydantic import BaseModel
import urllib.parse

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/api/login")
async def api_login(data: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    stmt = select(UserModel).where(UserModel.username == data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or user.password_hash != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Set session
    request.session["user_id"] = user.id
    return {"success": True, "message": "Logged in"}

@router.get("/authorize")
async def authorize_page(request: Request, db: AsyncSession = Depends(get_db)):
    user_id = request.session.get("user_id")
    
    # 1. If not logged in, redirect to Frontend Login
    if not user_id:
        # Construct current URL to pass as 'next'
        params = dict(request.query_params)
        next_url = str(request.url)
        encoded_next = urllib.parse.quote(next_url)
        frontend_login_url = f"http://localhost:5173/login?next={encoded_next}"
        return RedirectResponse(frontend_login_url)

    # 2. If logged in, check user validity
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    if not user:
        request.session.clear()
        return RedirectResponse(f"http://localhost:5173/login?next={urllib.parse.quote(str(request.url))}")

    # 3. If logged in, Redirect to Frontend Consent Page
    # Pass original params to the frontend consent page
    # Frontend will identify the client and ask user for approval
    # The Frontend will then POST back to /authorize with confirm=true
    
    params = dict(request.query_params)
    query_string = urllib.parse.urlencode(params)
    frontend_consent_url = f"http://localhost:5173/consent?{query_string}"
    return RedirectResponse(frontend_consent_url)


@router.post("/authorize")
async def authorize_confirm(request: Request, db: AsyncSession = Depends(get_db)):
    # This endpoint is called by the Frontend Consent Page
    user_id = request.session.get("user_id")
    if not user_id:
         raise HTTPException(status_code=401, detail="Not authenticated")
    
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    # Helper to parse form or JSON. Frontend likely sends JSON.
    try:
        data = await request.json()
    except:
        form = await request.form()
        data = dict(form)
    
    # Transform to AioAuth Request
    # Note: Query params for OAuth (client_id, etc) should be in the body now 
    # or passed along?
    # Standard aioauth expects them in query or body.
    # We construct aioauth request with the data we received.
    
    aio_request = AioAuthRequest(
        method=request.method,
        query=data, # Treat body data as query params for aioauth logic if needed, or put in post
        post=data,
        headers=dict(request.headers),
        user=user,
        url=str(request.url)
    )
    
    # Create authorization response (generates code)
    # This will check if 'response_type' etc are valid
    response = await server.create_authorization_response(aio_request)
    
    # If redirect (Code generated), we return the redirect URL to frontend
    # so frontend can redirect the browser to the Client
    if response.status_code == 302:
        return {"redirect_to": response.headers["Location"]}
    
    # If error
    return JSONResponse(content=response.content, status_code=response.status_code)

@router.post("/token")
async def token(request: Request):
    form = await request.form()
    aio_request = AioAuthRequest(
        method=request.method,
        query=dict(request.query_params),
        post=dict(form),
        headers=dict(request.headers),
        url=str(request.url)
    )
    
    response = await server.create_token_response(aio_request)
    return JSONResponse(content=response.content, status_code=response.status_code)

@router.get("/protected")
async def protected_resource(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    scheme, _, param = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token scheme")
        
    token = await server.storage.get_token(request=None, access_token=param)
    
    if not token or token.revoked:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return {"message": "Hello, this is a protected resource!", "user_id": token.client_id}
