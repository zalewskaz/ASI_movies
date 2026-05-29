import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'
load_dotenv(dotenv_path=env_path)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WATCHMODE_API_KEY = os.getenv("WATCHMODE_API_KEY")

if not TMDB_API_KEY or not WATCHMODE_API_KEY:
    raise ValueError("Missing API Keys in .env file.")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "dev_user")
DB_PASS = os.getenv("DB_PASS", "dev_pass")
DB_NAME = os.getenv("DB_NAME", "movie_db")
DB_PORT = os.getenv("DB_PORT", "5432")