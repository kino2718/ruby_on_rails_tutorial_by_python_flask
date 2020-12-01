import pytest

SUCCESS = 200

def test_should_get_home(client):
    response = client.get('/static_pages/home')
    assert response.status_code==SUCCESS

def test_should_get_help(client):
    response = client.get('/static_pages/help')
    assert response.status_code==SUCCESS

def test_should_get_about(client):
    response = client.get('/static_pages/about')
    assert response.status_code==SUCCESS
