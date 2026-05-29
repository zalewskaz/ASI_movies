import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2.extras import RealDictCursor
from config import DB_HOST, DB_USER, DB_PASS, DB_NAME, DB_PORT
import logging

app = FastAPI(title="ASI Movies API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_CONFIG = {
    "dbname": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS,
    "host": DB_HOST,
    "port": DB_PORT
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)


@app.get("/api/movies")
def get_movies(
    region: str = Query(None),
    platform: list[str] = Query(None) 
):
    logging.info(f"Zapytanie GET /api/movies | Filtry -> region: {region}, platform: {platform}")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if not region and not platform:
            cursor.execute("SELECT tmdb_id, title, year, poster_path, user_rating, critic_score, runtime FROM movies ORDER BY user_rating DESC;")
        else:
            query = """
                SELECT DISTINCT m.tmdb_id, m.title, m.year, m.poster_path, m.user_rating, m.critic_score, m.runtime 
                FROM movies m
                JOIN streaming s ON m.tmdb_id = s.tmdb_id
                WHERE 1=1
            """
            params = []
            if region:
                query += " AND UPPER(s.region) = UPPER(%s)"
                params.append(region)
            
            if platform:
                placeholders = ', '.join(['%s'] * len(platform))
                query += f" AND UPPER(s.service_name) IN ({placeholders})"
                
                params.extend([p.upper() for p in platform])
                
            query += " ORDER BY m.user_rating DESC;"
            cursor.execute(query, tuple(params))
            
        movies = cursor.fetchall()
        logging.info(f"Pomyślnie pobrano {len(movies)} filmów z bazy danych.")
        
        cursor.close()
        conn.close()
        return movies
    except Exception as e:
        logging.error(f"Błąd bazy danych w GET /api/movies: {str(e)}")
        raise HTTPException(status_code=500, detail="Wystąpił wewnętrzny błąd bazy danych.")


@app.get("/api/filters/platforms")
def get_unique_platforms():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT service_name FROM streaming ORDER BY service_name;")
        platforms = [row['service_name'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        return platforms
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd bazy danych: {str(e)}")


@app.get("/api/filters/regions")
def get_unique_regions():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT region FROM streaming ORDER BY region;")
        regions = [row['region'] for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        return regions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd bazy danych: {str(e)}")

@app.get("/api/stats/platforms-charts")
def get_platform_chart_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT service_name, COUNT(tmdb_id) as movie_count 
            FROM streaming 
            GROUP BY service_name 
            ORDER BY movie_count DESC
            LIMIT 10;
        """)
        chart_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return chart_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd bazy danych: {str(e)}")

@app.get("/api/stats/ratings/users")
def get_user_ratings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.service_name, AVG(m.user_rating) as avg_rating 
        FROM streaming s
        JOIN movies m ON s.tmdb_id = m.tmdb_id
        WHERE m.user_rating > 0
        GROUP BY s.service_name
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/stats/ratings/critics")
def get_critic_ratings():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.service_name, AVG(m.critic_score) as avg_rating 
        FROM streaming s
        JOIN movies m ON s.tmdb_id = m.tmdb_id
        WHERE m.critic_score > 0
        GROUP BY s.service_name
    """)
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    return data

@app.get("/api/stats/prices")
def get_prices(region: str = Query(...)): 
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT service_name, ROUND(AVG(price)::numeric, 2) as average_price
            FROM streaming
            WHERE price > 0 AND UPPER(region) = UPPER(%s)
            GROUP BY service_name 
            ORDER BY average_price ASC;
        """

        cursor.execute(query, (region,))
        data = cursor.fetchall()
        cursor.close()
        conn.close()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd bazy danych: {str(e)}")
