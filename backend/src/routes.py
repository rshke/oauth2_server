from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from src.oauth import server
from src.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aioauth.requests import Request as AioAuthRequest, Post, Query
from aioauth.config import Settings as AioAuthSettings
from src.models import User as UserModel
from pydantic import BaseModel
import urllib.parse
from dataclasses import fields

# Configure AioAuth settings for local dev
aio_settings = AioAuthSettings(
    INSECURE_TRANSPORT=True,
    TOKEN_EXPIRES_IN=3600,
)

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


@router.post("/login")
async def login_page_post(request: Request):
    form = await request.form()
    username = form.get("username")
    password = form.get("password")
    redirect_uri = request.query_params.get("redirect_uri")  # preserve redirect_uri

    async with SessionLocal() as session:
        from src.auth.service import auth_service

        # auth_service is now a global instance, we just pass the session for context
        user = await auth_service.authenticate_user(username, password, session=session)

        if user:
            request.session["user"] = {"id": user.id, "username": user.username}
            if redirect_uri:
                return RedirectResponse(url=redirect_uri, status_code=303)
            return RedirectResponse(url="/", status_code=303)

        # simple check failed
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Invalid credentials",
                "redirect_uri": redirect_uri,
            },
        )


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
        return RedirectResponse(
            f"http://localhost:5173/login?next={urllib.parse.quote(str(request.url))}"
        )

    # 3. If logged in, Redirect to Frontend Consent Page
    # Pass original params to the frontend consent page
    # Frontend will identify the client and ask user for approval
    # The Frontend will then POST back to /authorize with confirm=true

    params = dict(request.query_params)
    query_string = urllib.parse.urlencode(params)
    frontend_consent_url = f"http://localhost:5173/consent?{query_string}"
    return RedirectResponse(frontend_consent_url)


def _filter_dataclass_data(dataclass_type, data: dict) -> dict:
    """Helper to filter dict data to match dataclass fields"""
    field_names = {f.name for f in fields(dataclass_type)}
    return {k: v for k, v in data.items() if k in field_names}


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
    aio_request = AioAuthRequest(
        method=request.method,
        query=Query(
            **_filter_dataclass_data(Query, data)
        ),  # Treat body data as query params for aioauth logic if needed
        post=Post(**_filter_dataclass_data(Post, data)),
        headers=dict(request.headers),
        url=str(request.url),
        settings=aio_settings,
    )
    aio_request.user = user

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
    print("DEBUG: Entering /token endpoint")
    form = await request.form()
    form_data = dict(form)
    print(f"DEBUG: form_data keys: {list(form_data.keys())}")
    query_data = dict(request.query_params)

    post_obj = Post(**_filter_dataclass_data(Post, form_data))
    print(f"DEBUG: Created Post object: {post_obj}, type: {type(post_obj)}")

    aio_request = AioAuthRequest(
        method=request.method,
        query=Query(**_filter_dataclass_data(Query, query_data)),
        post=post_obj,
        headers=dict(request.headers),
        url=str(request.url),
        settings=aio_settings,
    )

    print(f"DEBUG: aio_request.post type: {type(aio_request.post)}")

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

    return {
        "message": "Hello, this is a protected resource!",
        "user_id": token.client_id,
    }
