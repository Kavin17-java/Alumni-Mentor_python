from flask import render_template
from app import create_app


def test_forms_and_home(tmp_path):
    app = create_app({'TESTING':True,'DATABASE_PATH':str(tmp_path/'front.db')})
    client = app.test_client()
    assert b'AlumniConnect' in client.get('/').data
    assert b'name="email"' in client.get('/login').data
    assert b'name="csrf_token"' in client.get('/register').data
    with app.test_request_context('/'):
        assert 'name="consent"' in render_template('profile.html',profile={})
        assert 'name="graduation_year"' in render_template('directory.html',alumni=[],matches=[],filters={})
