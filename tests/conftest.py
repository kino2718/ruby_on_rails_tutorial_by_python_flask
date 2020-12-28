import os
import tempfile

import pytest
from sampleapp import create_app


@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
    })

    yield app


@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def are_same_templates():
    def f(ref, contents):
        import re
        # meta tagのcsrf-tokenを取り除く
        ref = re.sub(r'<meta name="csrf-token" content=".*" />', r'', ref)
        contents = re.sub(r'<meta name="csrf-token" content=".*" />', r'', contents)
        return ref == contents

    return f
