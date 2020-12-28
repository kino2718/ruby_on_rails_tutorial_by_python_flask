from flask import render_template

def test_layout_links(client, are_same_templates):
    with client:
        response = client.get('/')
        assert are_same_templates(
            render_template('static_pages/home.html'),
            response.data.decode(encoding='utf-8'))
        #assert False

        el = '<a href="/"'.encode(encoding='utf-8')
        assert response.data.count(el) == 2
        el = '<a href="/help"'.encode(encoding='utf-8')
        assert response.data.count(el) == 1
        el = '<a href="/about"'.encode(encoding='utf-8')
        assert response.data.count(el) == 1
        el = '<a href="/contact"'.encode(encoding='utf-8')
        assert response.data.count(el) == 1
