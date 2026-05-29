CREATE TABLE IF NOT EXISTS movies (
    tmdb_id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    year INTEGER,
    poster_path VARCHAR(255),
    user_rating REAL,
    critic_score REAL,
    runtime INTEGER
);

CREATE TABLE IF NOT EXISTS streaming (
    row_id SERIAL PRIMARY KEY,
    tmdb_id INTEGER REFERENCES movies(tmdb_id),
    service_name VARCHAR(255),
    region VARCHAR(10),
    price REAL
);