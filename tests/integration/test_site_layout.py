from flask import render_template, url_for

def test_layout_links(client):
    with client:
        response = client.get('/')
        assert response.data == \
            render_template('static_pages/home.html').encode(encoding='utf-8')
        el = '<a href="/"'.encode(encoding='utf-8')
        assert response.data.count(el) == 2
        el = '<a href="/help"'.encode(encoding='utf-8')
        assert response.data.count(el) == 1
        el = '<a href="/about"'.encode(encoding='utf-8')
        assert response.data.count(el) == 1
        el = '<a href="/contact"'.encode(encoding='utf-8')
        assert response.data.count(el) == 1
