from aioauth.server import AuthorizationServer
from aioauth.storage import BaseStorage
from aioauth.requests import Request
from aioauth.models import Token, Client, AuthorizationCode
from src.database import get_db, SessionLocal
from src.models import (
    Token as TokenModel,
    Client as ClientModel,
    AuthorizationCode as CodeModel,
)
from sqlalchemy import select
from typing import Optional
from datetime import datetime, timezone
import time


class SQLAlchemyStorage(BaseStorage):
    async def get_client(
        self, request: Request, client_id: str, client_secret: Optional[str] = None
    ) -> Optional[Client]:
        async with SessionLocal() as session:
            stmt = select(ClientModel).where(ClientModel.client_id == client_id)
            if client_secret:
                stmt = stmt.where(ClientModel.client_secret == client_secret)
            result = await session.execute(stmt)
            client_model = result.scalar_one_or_none()
            if client_model:
                return client_model.to_aioauth_client()
        return None

    async def create_token(
        self,
        request: Request,
        client_id: str,
        scope: str,
        access_token: str,
        refresh_token: str,
    ) -> Token:
        async with SessionLocal() as session:
            token = TokenModel(
                client_id=client_id,
                scope=scope,
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=300,
                issued_at=int(datetime.now(tz=timezone.utc).timestamp()),
                user_id=getattr(request, "user", None).id
                if getattr(request, "user", None)
                else None,
            )
            session.add(token)
            await session.commit()
            return token.to_aioauth_token()

    async def get_token(
        self, request: Request, access_token: str, refresh_token: Optional[str] = None
    ) -> Optional[Token]:
        async with SessionLocal() as session:
            stmt = select(TokenModel).where(TokenModel.access_token == access_token)
            if refresh_token:
                stmt = stmt.where(TokenModel.refresh_token == refresh_token)
            result = await session.execute(stmt)
            token_model = result.scalar_one_or_none()
            if token_model:
                return token_model.to_aioauth_token()
        return None

    async def create_authorization_code(
        self,
        *,
        request: Request,
        client_id: str,
        scope: str,
        response_type: str,
        redirect_uri: str,
        code: str,
        code_challenge_method: Optional[str] = None,  # Type alias string
        code_challenge: Optional[str] = None,
        nonce: Optional[str] = None,
    ) -> AuthorizationCode:
        print(
            f"DEBUG: Saving auth code: {code} for client: {client_id}, redirect_uri: {redirect_uri}"
        )
        try:
            async with SessionLocal() as session:
                auth_code = CodeModel(
                    code=code,
                    client_id=client_id,
                    redirect_uri=redirect_uri,
                    response_type=response_type,
                    scope=scope,
                    auth_time=int(time.time()),
                    expires_in=600,
                    code_challenge=code_challenge,
                    code_challenge_method=code_challenge_method,
                    nonce=nonce,
                    user_id=getattr(request, "user", None).id
                    if getattr(request, "user", None)
                    else None,
                )
                session.add(auth_code)
                await session.commit()
                print("DEBUG: Auth code saved successfully")
                return auth_code.to_aioauth_code()
        except Exception as e:
            import logging

            logging.error(f"Error creating auth code: {e}")
            import traceback

            logging.error(traceback.format_exc())
            raise e

    async def get_authorization_code(
        self, request: Request, client_id: str, code: str
    ) -> Optional[AuthorizationCode]:
        print(f"DEBUG: Retrieving auth code: {code} for client: {client_id}")
        async with SessionLocal() as session:
            stmt = select(CodeModel).where(
                CodeModel.code == code, CodeModel.client_id == client_id
            )
            result = await session.execute(stmt)
            code_model = result.scalar_one_or_none()
            if code_model:
                print(f"DEBUG: Found auth code: {code_model.code}")
                return code_model.to_aioauth_code()
            else:
                print("DEBUG: Auth code not found")
        return None

    async def delete_authorization_code(
        self, request: Request, client_id: str, code: str
    ):
        async with SessionLocal() as session:
            stmt = select(CodeModel).where(
                CodeModel.code == code, CodeModel.client_id == client_id
            )
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

    async def get_id_token(
        self,
        request: Request,
        client_id: str,
        scope: str,
        response_type: str,
        redirect_uri: str,
        nonce: str,
    ) -> str:
        # Simple ID token implementation for OpenID Connect if needed, else optional
        return "dummy_id_token"


storage = SQLAlchemyStorage()
server = AuthorizationServer(storage=storage)
