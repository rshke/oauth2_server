"""seed_data

Revision ID: bea5b2e1e7b9
Revises: 2ff22cfe6d80
Create Date: 2026-02-07 12:13:29.570045

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bea5b2e1e7b9"
down_revision: Union[str, Sequence[str], None] = "2ff22cfe6d80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Insert seed data."""
    # Define tables with necessary columns
    clients_table = sa.table(
        "clients",
        sa.column("client_id", sa.String),
        sa.column("client_secret", sa.String),
        sa.column("grant_types", sa.String),
        sa.column("response_types", sa.String),
        sa.column("scope", sa.String),
        sa.column("redirect_uris", sa.String),
    )

    users_table = sa.table(
        "users",
        sa.column("username", sa.String),
        sa.column("password_hash", sa.String),
    )

    # Insert data idempotently
    bind = op.get_bind()

    # helper to check existence
    def entry_exists(table, column, value):
        query = sa.text(f"SELECT 1 FROM {table} WHERE {column} = :value")
        return bind.execute(query, {"value": value}).scalar() is not None

    # Calculate hash dynamically
    from passlib.context import CryptContext

    pwd_context = CryptContext(
        schemes=["argon2"],
        deprecated="auto",
        argon2__rounds=3,
        argon2__memory_cost=65536,
        argon2__parallelism=4,
    )
    demo_password_hash = pwd_context.hash("demo")

    clients_data = [
        {
            "client_id": "frontend_client",
            "client_secret": "secret",
            "grant_types": "authorization_code",
            "response_types": "code",
            "scope": "read",
            "redirect_uris": "http://localhost:5173/callback",
        },
        {
            "client_id": "demo_client",
            "client_secret": "demo_secret",
            "grant_types": "authorization_code",
            "response_types": "code",
            "scope": "read",
            "redirect_uris": "http://localhost:3000/callback",
        },
    ]

    users_data = [
        {"username": "demo", "password_hash": demo_password_hash},
    ]

    for client in clients_data:
        if not entry_exists("clients", "client_id", client["client_id"]):
            op.bulk_insert(clients_table, [client])

    for user in users_data:
        if not entry_exists("users", "username", user["username"]):
            op.bulk_insert(users_table, [user])
        else:
            # Update password if user exists (to migrate existing plain text passwords)
            op.execute(
                users_table.update()
                .where(users_table.c.username == user["username"])
                .values(password_hash=user["password_hash"])
            )


def downgrade() -> None:
    """Downgrade schema - Remove seed data."""
    op.execute(
        "DELETE FROM clients WHERE client_id IN ('frontend_client', 'demo_client')"
    )
    op.execute("DELETE FROM users WHERE username = 'demo'")
