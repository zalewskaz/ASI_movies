from fastapi.testclient import TestClient
from unittest.mock import patch
from backend.api import app

client = TestClient(app)

# get unique regions
@patch('backend.api.get_db_connection')
def test_get_unique_regions(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'region': 'US'}, {'region': 'PL'}, {'region': 'GB'}]
    
    response = client.get("/api/filters/regions")
    
    assert response.status_code == 200
    assert response.json() == ['US', 'PL', 'GB']


# get unique platforms
@patch('backend.api.get_db_connection')
def test_get_unique_platforms(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'service_name': 'Netflix'}, {'service_name': 'Max'}]
    
    response = client.get("/api/filters/platforms")
    
    assert response.status_code == 200
    assert response.json() == ['Netflix', 'Max']


# get movies (no filters)
@patch('backend.api.get_db_connection')
def test_get_movies_no_filters(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'tmdb_id': 1, 'title': 'Incepcja', 'year': 2010}]
    
    response = client.get("/api/movies")
    
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['title'] == 'Incepcja'


# get movies (with filters - simulating frontend query)
@patch('backend.api.get_db_connection')
def test_get_movies_with_filters(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'tmdb_id': 2, 'title': 'Diuna', 'year': 2021}]
    
    response = client.get("/api/movies?region=PL&platform=Max")
    
    assert response.status_code == 200
    assert response.json()[0]['title'] == 'Diuna'
    mock_cursor.execute.assert_called_once()


# edgecase: pusta lista platform
def test_get_movies_empty_platforms():
    response = client.get("/api/movies?platform=")
    
    assert response.status_code == 200
    assert response.json() == []


# statystyki rozkladu platform (wykres)
@patch('backend.api.get_db_connection')
def test_get_platform_distribution(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'service_name': 'Netflix', 'movie_count': 15}]
    
    response = client.get("/api/stats/platform-distribution")
    
    assert response.status_code == 200
    assert response.json()[0]['movie_count'] == 15


# statystyki user scores (wykres)
@patch('backend.api.get_db_connection')
def test_get_user_ratings(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'service_name': 'Amazon Prime', 'avg_rating': 7.5}]
    
    response = client.get("/api/stats/ratings/users")
    
    assert response.status_code == 200
    assert response.json()[0]['avg_rating'] == 7.5


# statystyki critic scores (wykres)
@patch('backend.api.get_db_connection')
def test_get_critic_ratings(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'service_name': 'Max', 'avg_rating': 82.0}]
    
    response = client.get("/api/stats/ratings/critics")
    
    assert response.status_code == 200
    assert response.json()[0]['avg_rating'] == 82.0


# statystyki avg cen (per region)
@patch('backend.api.get_db_connection')
def test_get_prices_with_region(mock_get_db_connection):
    mock_cursor = mock_get_db_connection.return_value.cursor.return_value
    mock_cursor.fetchall.return_value = [{'service_name': 'Netflix', 'average_price': 43.0}]
    
    response = client.get("/api/stats/prices?region=US")
    
    assert response.status_code == 200
    assert response.json()[0]['average_price'] == 43.0


# edgecase: bez podania regionu przy cenach
def test_get_prices_missing_region():
    # powinien byc error 422 (Unprocessable Entity)
    response = client.get("/api/stats/prices")
    
    assert response.status_code == 422