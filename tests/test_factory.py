from sampleapp import create_app


def test_config():
    assert not create_app().testing
    assert create_app({'TESTING': True}).testing


def test_root(client):
    response = client.get('/')
    assert response.status_code==200
    assert b'Home' in response.data
