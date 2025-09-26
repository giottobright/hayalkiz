import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load default .env, then optionally keys.env if present
load_dotenv()
if os.path.exists("keys.env"):
    load_dotenv("keys.env", override=True)


class Settings(BaseModel):
    telegram_bot_token: str
    openai_api_key: str
    flux_api_key: str | None = None
    flux_api_url: str | None = None
    webapp_url: str = "http://localhost:5173"
    database_path: str = os.path.join("data", "app.db")

    class Config:
        arbitrary_types_allowed = True


def get_settings() -> Settings:
    return Settings(
        telegram_bot_token=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        flux_api_key=os.getenv("FLUX_API_KEY"),
        flux_api_url=os.getenv("FLUX_API_URL", "https://api.bfl.ai/v1/flux-kontext-pro"),
        webapp_url=os.getenv("WEBAPP_URL", "http://localhost:5173"),
        database_path=os.getenv("DATABASE_PATH", os.path.join("data", "app.db")),
    )
