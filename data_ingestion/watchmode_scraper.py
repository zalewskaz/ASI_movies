import os
import json
import logging
import requests
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s'
)

load_dotenv()

def get_watchmode_id_from_tmdb(tmdb_id: str, is_tv_show: bool = False) -> str:
    api_key = os.getenv("WATCHMODE_API_KEY")
    if not api_key:
        return None

    search_field = "tmdb_tv_id" if is_tv_show else "tmdb_movie_id"
    
    url = "https://api.watchmode.com/v1/search/"
    params = {
        "apiKey": api_key,
        "search_field": search_field,
        "search_value": tmdb_id
    }
    
    logging.info(f"Szukam Watchmode ID dla TMDB ID: {tmdb_id} ({search_field})...")
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data.get("title_results"):
            watchmode_id = str(data["title_results"][0]["id"])
            logging.info(f"Znaleziono odpowiednik w Watchmode! ID: {watchmode_id}")
            return watchmode_id
        else:
            logging.warning(f"Nie znaleziono tytułu dla TMDB ID {tmdb_id} w Watchmode.")
            return None

    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd podczas translacji ID: {e}")
        return None


def fetch_watchmode_title_details(watchmode_id: str) -> dict:
    api_key = os.getenv("WATCHMODE_API_KEY")
    url = f"https://api.watchmode.com/v1/title/{watchmode_id}/details/"
    params = {
        "apiKey": api_key,
        "append_to_response": "sources"
    }

    logging.info(f"Pobieranie platform VOD dla Watchmode ID: {watchmode_id}...")

    try:
        response = requests.get(url, params=params)
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Błąd podczas pobierania szczegółów tytułu: {e}")
        return None


if __name__ == "__main__":
    tmdb_sample_id = "603" 
    
    wm_id = get_watchmode_id_from_tmdb(tmdb_sample_id, is_tv_show=False)

    if wm_id:
        movie_data = fetch_watchmode_title_details(wm_id)

        if movie_data:
            os.makedirs("raw_data", exist_ok=True)
            file_path = f"raw_data/tmdb_{tmdb_sample_id}_watchmode.json"
            
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(movie_data, f, indent=4, ensure_ascii=False)
                
            logging.info(f"Zapisano dane do: {file_path}")
    else:
        logging.error("Przerwano proces: Nie można zmapować TMDB ID na Watchmode ID.")