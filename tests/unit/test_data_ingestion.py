import pytest
from unittest.mock import patch, MagicMock
from data_ingestion.tmdb_client import get_popular_movies
from data_ingestion.watchmode_scraper import get_watchmode_id_from_tmdb, fetch_watchmode_title_details
from data_ingestion.data_pipeline import run_pipeline

# TMDB
@patch('data_ingestion.tmdb_client.requests.get')
def test_get_popular_movies(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "results": [
            {"id": 111, "title": "Testowy Film A", "release_date": "2023-01-01"},
            {"id": 222, "title": "Testowy Film B", "release_date": "2023-02-02"}
        ]
    }
    mock_get.return_value = mock_response

    movies = get_popular_movies(limit=2)

    assert len(movies) == 2
    assert movies[0]['title'] == "Testowy Film A"
    assert movies[1]['id'] == 222
    mock_get.assert_called()

# watchmode
@patch('data_ingestion.watchmode_scraper.requests.get')
def test_get_watchmode_id_from_tmdb_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "title_results": [
            {"id": 9999, "tmdb_id": 111, "tmdb_type": "movie"}
        ]
    }
    mock_get.return_value = mock_response

    watchmode_id = get_watchmode_id_from_tmdb(111)
    
    assert str(watchmode_id) == '9999'


@patch('data_ingestion.watchmode_scraper.requests.get')
def test_get_watchmode_id_from_tmdb_not_found(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"title_results": []}
    mock_get.return_value = mock_response

    watchmode_id = get_watchmode_id_from_tmdb(999999)
    
    assert watchmode_id is None


@patch('data_ingestion.watchmode_scraper.requests.get')
def test_fetch_watchmode_title_details(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "year": 2023,
        "sources": [
            {"name": "Netflix", "region": "US", "price": 9.99},
            {"name": "Netflix", "region": "US", "price": 14.99},
            {"name": "Max", "region": "US", "price": 15.99}
        ]
    }
    mock_get.return_value = mock_response

    wm_details = fetch_watchmode_title_details(9999)
    
    assert isinstance(wm_details, dict)
    
    sources = wm_details.get("sources", [])
    assert len(sources) > 0
    names = [s['name'] for s in sources]
    assert "Netflix" in names

# entire pipeline
@patch('data_ingestion.data_pipeline.get_db_connection')
@patch('data_ingestion.data_pipeline.fetch_watchmode_title_details')
@patch('data_ingestion.data_pipeline.get_watchmode_id_from_tmdb')
@patch('data_ingestion.data_pipeline.get_popular_movies')
@patch('data_ingestion.data_pipeline.execute_values')
def test_run_pipeline(mock_execute_values, mock_tmdb, mock_wm_id, mock_wm_details, mock_db):
    mock_tmdb.return_value = [{'id': 100, 'title': 'Matrix', 'release_date': '1999', 'vote_average': 8.7, 'vote_count': 10000, 'poster_path': '/matrix.jpg'}]
    mock_wm_id.return_value = 500
    
    mock_wm_details.return_value = {
        'year': 1999,
        'sources': [{'name': 'Netflix', 'region': 'US', 'price': 10.0}]
    }

    mock_conn = mock_db.return_value
    mock_cursor = mock_conn.cursor.return_value

    run_pipeline()

    mock_tmdb.assert_called_once()
    mock_wm_id.assert_called_once()
    mock_wm_details.assert_called_once_with(500)
    
    assert mock_cursor.execute.call_count >= 1
    mock_execute_values.assert_called_once()
    mock_conn.commit.assert_called_once()