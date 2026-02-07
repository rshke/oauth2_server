from typing import Protocol, List, Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import User
from src.auth.security import verify_password
import logging


# 1. Define the Interface (Protocol)
class AuthBackend(Protocol):
    async def authenticate(
        self, username: str, password: str, session: Optional[AsyncSession] = None
    ) -> Optional[User]: ...


# 2. Implement Local Database Backend
class LocalAuthBackend:
    # No __init__ needed with session

    async def authenticate(
        self, username: str, password: str, session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        if not session:
            logging.error("LocalAuthBackend requires a database session")
            return None

        try:
            # Check Local DB
            result = await session.execute(
                select(User).where(User.username == username)
            )
            user = result.scalars().first()

            if user and verify_password(password, user.password_hash):
                return user
            return None
        except Exception as e:
            logging.error(f"Local auth error: {e}")
            return None


# 3. Example: How you would add LDAP (Pseudocode)
class LDAPAuthBackend:
    def __init__(self, ldap_server_url: str):
        self.ldap_url = ldap_server_url

    async def authenticate(
        self, username: str, password: str, session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        # logic to bind to LDAP server
        # if success, return User(...)
        logging.info(f"Checking LDAP for {username}...")
        return None


# 4. The Main Service (Composite)
class AuthenticationService:
    def __init__(self, backends: List[AuthBackend]):
        self.backends = backends

    async def authenticate_user(
        self, username: str, password: str, session: Optional[AsyncSession] = None
    ) -> Optional[User]:
        """Iterates through all configured backends until one succeeds."""
        for backend in self.backends:
            # Pass session to all backends (some might ignore it)
            user = await backend.authenticate(username, password, session=session)
            if user:
                return user
        return None


# Global Instance
auth_service = AuthenticationService(
    backends=[
        LocalAuthBackend(),
        # LDAPAuthBackend("ldap://company.com"),
    ]
)
