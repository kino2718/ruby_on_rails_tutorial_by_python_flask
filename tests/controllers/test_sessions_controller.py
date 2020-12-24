SUCCESS = 200

def test_should_get_new(client):
    response = client.get('/login')
    assert response.status_code==SUCCESS
