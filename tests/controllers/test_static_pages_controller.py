import pytest

SUCCESS = 200
base_title = "Ruby on Rails Tutorial Sample App"

def test_should_get_home(client):
    response = client.get('/')
    assert response.status_code==SUCCESS
    assert f"<title>{base_title}</title>".encode(encoding='utf-8') \
        in response.data

def test_should_get_help(client):
    response = client.get('/help')
    assert response.status_code==SUCCESS
    assert f"<title>Help | {base_title}</title>".encode(encoding='utf-8') \
        in response.data

def test_should_get_about(client):
    response = client.get('/about')
    assert response.status_code==SUCCESS
    assert f"<title>About | {base_title}</title>".encode(encoding='utf-8') \
        in response.data

def test_should_get_contact(client):
    response = client.get('/contact')
    assert response.status_code==SUCCESS
    assert f"<title>Contact | {base_title}</title>".encode(encoding='utf-8') \
        in response.data
