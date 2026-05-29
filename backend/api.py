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


# Główny endpoint: pobiera wszystkie filmy lub filtruje je na bieżąco
@app.get("/api/movies")
def get_movies(
    region: str = Query(None),
    platform: str = Query(None)
):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Jeśli użytkownik nie wybrał filtrów, pobieramy po prostu wszystkie filmy
        if not region and not platform:
            cursor.execute("SELECT tmdb_id, title, year, poster_path, user_rating, critic_score, runtime FROM movies ORDER BY user_rating DESC;")
        else:
            # Jeśli filtry są włączone, łączymy tabele (JOIN)
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
                query += " AND UPPER(s.service_name) = UPPER(%s)"
                params.append(platform)
                
            query += " ORDER BY m.user_rating DESC;"
            cursor.execute(query, tuple(params))
            
        movies = cursor.fetchall()
        cursor.close()
        conn.close()
        return movies
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd bazy danych: {str(e)}")


# Pobiera unikalne platformy streamingowe do listy rozwijanej
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


# Pobiera unikalne regiony do listy rozwijanej
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

# Dane do wykresu słupkowego 
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
