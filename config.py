import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
env_path = BASE_DIR / '.env'

load_dotenv(dotenv_path=env_path)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
WATCHMODE_API_KEY = os.getenv("WATCHMODE_API_KEY")

if not TMDB_API_KEY:
    raise ValueError("Missing TMDB_API_KEY in .env file.")

if not WATCHMODE_API_KEY:
    raise ValueError("Missing WATCHMODE_API_KEY in .env file.")
