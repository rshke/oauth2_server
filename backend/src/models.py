from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base
from aioauth.models import Client as AioAuthClient
from aioauth.models import Token as AioAuthToken
from aioauth.models import AuthorizationCode as AioAuthAuthorizationCode
from aioauth.types import GrantType, ResponseType
from typing import Optional, List


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)


class Client(Base):
    __tablename__ = "clients"

    client_id = Column(String, primary_key=True, index=True)
    client_secret = Column(String)
    grant_types = Column(String)  # Stored as comma-separated string or JSON
    response_types = Column(String)
    scope = Column(String)
    redirect_uris = Column(String)

    def to_aioauth_client(self) -> AioAuthClient:
        return AioAuthClient(
            client_id=self.client_id,
            client_secret=self.client_secret,
            grant_types=[g for g in self.grant_types.split(",")]
            if self.grant_types
            else [],
            response_types=[r for r in self.response_types.split(",")]
            if self.response_types
            else [],
            scope=self.scope,
            redirect_uris=self.redirect_uris.split(",") if self.redirect_uris else [],
        )


class Token(Base):
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    access_token = Column(String, unique=True, index=True)
    refresh_token = Column(String, unique=True, index=True)
    scope = Column(String)
    issued_at = Column(Integer)
    expires_in = Column(Integer)
    client_id = Column(String, ForeignKey("clients.client_id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    revoked = Column(Boolean, default=False)

    def to_aioauth_token(self) -> AioAuthToken:
        return AioAuthToken(
            access_token=self.access_token,
            refresh_token=self.refresh_token,
            scope=self.scope,
            issued_at=self.issued_at,
            expires_in=self.expires_in,
            refresh_token_expires_in=900,
            client_id=self.client_id,
            revoked=self.revoked,
        )


class AuthorizationCode(Base):
    __tablename__ = "authorization_codes"

    code = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.client_id"))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    redirect_uri = Column(String)
    response_type = Column(String)
    scope = Column(String)
    auth_time = Column(Integer)
    expires_in = Column(Integer)
    code_challenge = Column(String, nullable=True)
    code_challenge_method = Column(String, nullable=True)
    nonce = Column(String, nullable=True)

    def to_aioauth_code(self) -> AioAuthAuthorizationCode:
        print(f"[debug] {self.code}")
        return AioAuthAuthorizationCode(
            code=self.code,
            client_id=self.client_id,
            redirect_uri=self.redirect_uri,
            response_type=self.response_type,
            scope=self.scope,
            auth_time=self.auth_time,
            expires_in=self.expires_in,
            code_challenge=self.code_challenge,
            code_challenge_method=self.code_challenge_method,
            nonce=self.nonce,
        )
