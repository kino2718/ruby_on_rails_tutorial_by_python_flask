import pytest
from main import app

SUCCESS = 200

def test_should_get_home():
    with app.test_client() as c:
        response = c.get('/static_pages/home')
        assert response.status_code==SUCCESS

def test_should_get_help():
    with app.test_client() as c:
        response = c.get('/static_pages/help')
        assert response.status_code==SUCCESS

def test_should_get_about():
    with app.test_client() as c:
        response = c.get('/static_pages/about')
        assert response.status_code==SUCCESS
