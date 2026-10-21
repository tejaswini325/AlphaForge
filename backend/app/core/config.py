import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    app_name: str = "AlphaForge"
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./alphaforge.db")
    artifact_dir: str = os.getenv("ARTIFACT_DIR", "./artifacts")
    frontend_origins: tuple[str, ...] = tuple(
        x.strip() for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173").split(",") if x.strip()
    )
    max_assets: int = int(os.getenv("MAX_ASSETS", "50"))
    max_history_days: int = int(os.getenv("MAX_HISTORY_DAYS", "3650"))

settings = Settings()
