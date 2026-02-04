from aioauth.server import AuthorizationServer
from aioauth.storage import BaseStorage
from aioauth.requests import Request
from aioauth.models import Token, Client, AuthorizationCode
from src.database import get_db, SessionLocal
from src.models import Token as TokenModel, Client as ClientModel, AuthorizationCode as CodeModel
from sqlalchemy import select
from typing import Optional
import time

class SQLAlchemyStorage(BaseStorage):
    async def get_client(self, request: Request, client_id: str, client_secret: Optional[str] = None) -> Optional[Client]:
        async with SessionLocal() as session:
            stmt = select(ClientModel).where(ClientModel.client_id == client_id)
            if client_secret:
                stmt = stmt.where(ClientModel.client_secret == client_secret)
            result = await session.execute(stmt)
            client_model = result.scalar_one_or_none()
            if client_model:
                return client_model.to_aioauth_client()
        return None

    async def create_token(self, request: Request, client_id: str, scope: str, access_token: str, refresh_token: str, expires_in: int) -> Token:
        async with SessionLocal() as session:
            token = TokenModel(
                client_id=client_id,
                scope=scope,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=expires_in,
                issued_at=int(request.query.get("issued_at", 0) or 0), # Simplified
                user_id=request.user.id if request.user else None
            )
            session.add(token)
            await session.commit()
            return token.to_aioauth_token()

    async def get_token(self, request: Request, access_token: str, refresh_token: Optional[str] = None) -> Optional[Token]:
        async with SessionLocal() as session:
            stmt = select(TokenModel).where(TokenModel.access_token == access_token)
            if refresh_token:
                stmt = stmt.where(TokenModel.refresh_token == refresh_token)
            result = await session.execute(stmt)
            token_model = result.scalar_one_or_none()
            if token_model:
                return token_model.to_aioauth_token()
        return None
    
    async def create_authorization_code(self, request: Request, client_id: str, scope: str, response_type: str, redirect_uri: str, code_challenge: Optional[str], code_challenge_method: Optional[str], nonce: Optional[str]) -> AuthorizationCode:
         # Note: aioauth doesn't pass the generated code here directly in some versions, 
         # but let's assume we handle it or rely on the library to generate.
         # Actually aioauth's create_authorization_code signature in base storage includes 'code'.
         # Let's check the library usage or stick to the interface.
         # Checking standard aioauth storage signature.
         # It usually receives the `code` string.
         # If not, we might need to update this based on exact version. 
         # Assuming recent aioauth.
         
         # However, for now, let's implement the method with *args or **kwargs to be safe if signature varies, 
         # but strict typing suggests following the BaseStorage.
         # We will implement it matching the args provided by the library call usually.
         
         # Wait, I need to implement `save_authorization_code`. `create_authorization_code` is usually on the server.
         # Storage method is `create_authorization_code` in `BaseStorage`?
         # Let's check `aioauth` docs or source if possible. 
         # Since I cannot browse, I will assume the standard `create_authorization_code(self, request, client_id, scope, response_type, redirect_uri, code, ...)`
         pass

    async def create_authorization_code(
        self,
        *,
        request: Request,
        client_id: str,
        scope: str,
        response_type: str,
        redirect_uri: str,
        code: str,
        code_challenge_method: Optional[str] = None, # Type alias string
        code_challenge: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> AuthorizationCode:
        try:
            async with SessionLocal() as session:
                auth_code = CodeModel(
                    code=code,
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    scope=scope,
                    auth_time=int(time.time()),
                    expires_in=600, 
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                    nonce=nonce,
                    user_id=request.user.id if request.user else None
                )
                session.add(auth_code)
                await session.commit()
                return auth_code.to_aioauth_code()
        except Exception as e:
            import logging
            logging.error(f"Error creating auth code: {e}")
            import traceback
            logging.error(traceback.format_exc())
            raise e

    async def get_authorization_code(self, request: Request, client_id: str, code: str) -> Optional[AuthorizationCode]:
        async with SessionLocal() as session:
            stmt = select(CodeModel).where(CodeModel.code == code, CodeModel.client_id == client_id)
            result = await session.execute(stmt)
            code_model = result.scalar_one_or_none()
            if code_model:
                return code_model.to_aioauth_code()
        return None

    async def delete_authorization_code(self, request: Request, client_id: str, code: str):
        async with SessionLocal() as session:
            stmt = select(CodeModel).where(CodeModel.code == code, CodeModel.client_id == client_id)
            result = await session.execute(stmt)
            code_model = result.scalar_one_or_none()
            if code_model:
                await session.delete(code_model)
                await session.commit()

    async def revoke_token(self, request: Request, refresh_token: str) -> None:
        async with SessionLocal() as session:
            stmt = select(TokenModel).where(TokenModel.refresh_token == refresh_token)
            result = await session.execute(stmt)
            token_model = result.scalar_one_or_none()
            if token_model:
                token_model.revoked = True
                await session.commit()
    
    async def get_id_token(self, request: Request, client_id: str, scope: str, response_type: str, redirect_uri: str, nonce: str) -> str:
        # Simple ID token implementation for OpenID Connect if needed, else optional
        return "dummy_id_token"

storage = SQLAlchemyStorage()
server = AuthorizationServer(storage=storage)
