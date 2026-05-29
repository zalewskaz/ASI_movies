import requests
import time
from config import TMDB_API_KEY

BASE_URL = "https://api.themoviedb.org/3"

def get_popular_movies(limit=10):
    url = f"{BASE_URL}/movie/popular"
    all_movies = []
    
    movies_per_page = 20
    pages_to_fetch = limit // movies_per_page
    
    for page in range(1, pages_to_fetch + 1):
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
            "page": page
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
            
        page_data = response.json()
        movies_on_page = page_data.get("results", [])
            
        if not movies_on_page:
            break
                
        all_movies.extend(movies_on_page)
        time.sleep(0.2)   

    return all_movies[:limit]
