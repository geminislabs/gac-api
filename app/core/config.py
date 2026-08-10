from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_SCHEME: str = "public"

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRES_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRES_DAYS: int = 7

    PASETO_SECRET_KEY: str

    # Entorno de demo de Nexus. Vive en otra EC2 y se alcanza por internet: su
    # API de operaciones (/internal/*) solo acepta la IP de salida de esta
    # instancia, y además exige el bearer.
    #
    # Sin valor por defecto a propósito para la URL: apuntar sin querer a
    # localhost daría un fallo de conexión confuso en vez de decir que falta
    # configurar. El secreto sí admite vacío para que los tests y el arranque
    # local no exijan credenciales reales; validate_nexus_demo_config() avisa.
    NEXUS_DEMO_OPS_URL: str = ""
    GATE_INTERNAL_SECRET: str = ""

    # Vigencia por defecto de una demo, en horas. 7 días, igual que el
    # DEMO_TTL_HOURS del entorno de demo.
    NEXUS_DEMO_DEFAULT_TTL_HOURS: int = 168

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()


def missing_nexus_demo_config() -> list[str]:
    """Ajustes que le faltan a la integración con el entorno de demo.

    No se aborta el arranque: gac-api hace muchas otras cosas y tumbar la API
    entera porque una funcionalidad no está configurada sería peor que el
    problema. Se avisa al arrancar —donde se ve— y los endpoints de demos
    responden con un mensaje explícito en vez de un 401 opaco del gate.
    """
    missing = []
    if not settings.NEXUS_DEMO_OPS_URL:
        missing.append("NEXUS_DEMO_OPS_URL")
    if not settings.GATE_INTERNAL_SECRET:
        missing.append("GATE_INTERNAL_SECRET")
    return missing
