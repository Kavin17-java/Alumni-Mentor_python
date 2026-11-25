from app import create_app

def test_home(tmp_path):
    app = create_app({'TESTING': True, 'DATABASE_PATH': str(tmp_path / 'test.db')})
    assert app.test_client().get('/').status_code == 200
