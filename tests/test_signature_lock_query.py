import os

os.environ.setdefault("SECRET_KEY", "test-secret-key-with-enough-length")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost:5432/test")
os.environ.setdefault("S3_ACCESS_KEY", "test")
os.environ.setdefault("S3_SECRET_KEY", "test")

from sqlalchemy.dialects import postgresql  # noqa: E402

from app.services.signatures import signature_service  # noqa: E402


def test_signature_lock_query_only_locks_contract_row() -> None:
    statement = signature_service._contract_for_signing_statement("token")
    sql = str(statement.compile(dialect=postgresql.dialect()))

    assert "LEFT OUTER JOIN" not in sql
    assert "FOR UPDATE OF" in sql
    assert "contracts" in sql

