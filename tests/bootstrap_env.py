"""Apply test-only environment defaults before app Settings() loads."""

import os

_TEST_ENV_DEFAULTS = {
    "DB_HOST": "localhost",
    "DB_PORT": "5432",
    "DB_USER": "test",
    "DB_PASSWORD": "test",
    "DB_NAME": "test",
    "DB_SCHEME": "gac",
    "JWT_SECRET": "test-jwt-secret-key-for-unit-tests",
    "JWT_ALGORITHM": "HS256",
    "PASETO_SECRET_KEY": "dGVzdC1wYXNldG8tc2VjcmV0LWtleS0zMmJ5dGVz",
}


def apply_test_env_defaults() -> None:
    for key, value in _TEST_ENV_DEFAULTS.items():
        os.environ.setdefault(key, value)


def bootstrap_test_runtime() -> None:
    apply_test_env_defaults()
    from sqlite_dialect import register_sqlite_dialect_compat

    register_sqlite_dialect_compat()
