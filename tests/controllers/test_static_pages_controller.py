import pytest

SUCCESS = 200
base_title = "Ruby on Rails Tutorial Sample App"

def test_should_get_home(client):
    response = client.get('/static_pages/home')
    assert response.status_code==SUCCESS
    assert f"<title>Home | {base_title}</title>".encode(encoding='utf-8') \
        in response.data

def test_should_get_help(client):
    response = client.get('/static_pages/help')
    assert response.status_code==SUCCESS
    assert f"<title>Help | {base_title}</title>".encode(encoding='utf-8') \
        in response.data

def test_should_get_about(client):
    response = client.get('/static_pages/about')
    assert response.status_code==SUCCESS
    assert f"<title>About | {base_title}</title>".encode(encoding='utf-8') \
        in response.data

def test_should_get_contact(client):
    response = client.get('/static_pages/contact')
    assert response.status_code==SUCCESS
    assert f"<title>Contact | {base_title}</title>".encode(encoding='utf-8') \
        in response.data
