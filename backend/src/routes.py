from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from src.oauth import server
from src.database import get_db, SessionLocal
from src.models import User, Client
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from aioauth.requests import Request as AioAuthRequest
from src.models import User as UserModel

router = APIRouter()

@router.get("/authorize", response_class=HTMLResponse)
async def authorize_page(request: Request):
    # Determine the current state from the query for rendering the form
    # In a real app, you would render a template
    return """
    <html>
        <body>
            <form method="POST">
                <label>Username: <input type="text" name="username"/></label>
                <label>Password: <input type="password" name="password"/></label>
                <input type="submit" value="Authorize"/>
            </form>
        </body>
    </html>
    """

@router.post("/authorize")
async def authorize(request: Request, db: AsyncSession = Depends(get_db)):
    form = await request.form()
    username = form.get("username")
    password = form.get("password") # In real app, verify hash
    
    # Simple user verification
    stmt = select(UserModel).where(UserModel.username == username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        # For demo, creating user if not exists or just failing
        if username:
            user = UserModel(username=username, password_hash="hash") 
            db.add(user)
            await db.commit()
        else:
            return HTMLResponse("Invalid credentials", status_code=401)
            
    # Create aioauth request
    # We need to adapt FastAPI request to aioauth request
    aio_request = AioAuthRequest(
        method=request.method,
        query=dict(request.query_params),
        post=dict(form),
        headers=dict(request.headers),
        user=user, # Pass the user object
        url=str(request.url) 
    )
    
    # The server.create_authorization_response will handle the logic
    # It internally calls storage.create_authorization_code if approved
    response = await server.create_authorization_response(aio_request)
    
    if response.status_code == 302:
        return RedirectResponse(response.headers["Location"], status_code=302)
    
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
    # Validate token
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    
    # token = auth_header.split(" ")[1]
    # In aioauth, we can use server.validate_access_token or similar logic usually,
    # but for simple verification we rely on the introspection or manual check via storage.
    
    # Note: A proper validation involves verifying the access token against the DB and expiry.
    # aioauth doesn't have a direct 'validate_request' high-level middleware easily accessible 
    # without instantiating a logic block, so we'll do a quick check via storage or build a dependency.
    
    # For this demo, let's manually verify against DB using storage logic logic locally 
    # or re-use storage method.
    
    # We'll need to parse the bearer token
    scheme, _, param = auth_header.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid token scheme")
        
    token = await server.storage.get_token(request=None, access_token=param)
    
    if not token or token.revoked: # Check expiry as well
        raise HTTPException(status_code=401, detail="Invalid or expired token")
        
    return {"message": "Hello, this is a protected resource!", "user_id": token.client_id}
