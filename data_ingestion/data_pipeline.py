import logging
import psycopg2
from psycopg2.extras import execute_values
from data_ingestion.tmdb_client import get_popular_movies
from data_ingestion.watchmode_scraper import get_watchmode_id_from_tmdb, fetch_watchmode_title_details
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_db_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Nie udało się połączyć z bazą danych: {e}")
        return None

def run_pipeline():
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()
    
    logging.info("Pobieram TOP 10 filmów z TMDB...")
    top_movies = get_popular_movies(limit=10)
    
    for movie in top_movies:
        tmdb_id = movie.get("id")
        title = movie.get("title")
        poster_path = movie.get("poster_path")
        
        logging.info(f"Przetwarzam: {title} (TMDB ID: {tmdb_id})")
        
        wm_id = get_watchmode_id_from_tmdb(str(tmdb_id), is_tv_show=False)
        if not wm_id:
            logging.warning(f"Pomijam {title} - brak odpowiednika w Watchmode.")
            continue
            
        wm_details = fetch_watchmode_title_details(wm_id)
        if not wm_details:
            logging.warning(f"Pomijam {title} - nie udało się pobrać szczegółów.")
            continue

        year = wm_details.get("year") if wm_details.get("year") is not None else 0
        user_rating = wm_details.get("user_rating") if wm_details.get("user_rating") is not None else 0.0
        raw_critic_score = wm_details.get("critic_score")
        critic_score = (raw_critic_score / 10.0) if raw_critic_score is not None else 0.0
        runtime = wm_details.get("runtime_minutes") if wm_details.get("runtime_minutes") is not None else 0   

        poster_path = movie.get("poster_path") if movie.get("poster_path") is not None else "placeholder.jpg"

        insert_movie_query = """
            INSERT INTO movies (tmdb_id, title, year, poster_path, user_rating, critic_score, runtime)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (tmdb_id) DO UPDATE SET 
                user_rating = EXCLUDED.user_rating,
                critic_score = EXCLUDED.critic_score;
        """
        cursor.execute(insert_movie_query, (tmdb_id, title, year, poster_path, user_rating, critic_score, runtime))
        
        sources = wm_details.get("sources", [])
        if sources:
            cheapest_sources = {}
            
            for source in sources:
                service_name = source.get("name")
                region = source.get("region")
                
                price = source.get("price") if source.get("price") is not None else 0.0
                
                key = (service_name, region)
                
                if key not in cheapest_sources or price < cheapest_sources[key]:
                    cheapest_sources[key] = price
            
            streaming_records = [
                (tmdb_id, service, reg, prc) 
                for (service, reg), prc in cheapest_sources.items()
            ]
            
            cursor.execute("DELETE FROM streaming WHERE tmdb_id = %s;", (tmdb_id,))
            
            insert_streaming_query = """
                INSERT INTO streaming (tmdb_id, service_name, region, price)
                VALUES %s;
            """
            execute_values(cursor, insert_streaming_query, streaming_records)
    conn.commit()
    cursor.close()
    conn.close()
    logging.info("Pipeline zakończony sukcesem. Dane zapisane w bazie.")

if __name__ == "__main__":
    run_pipeline()