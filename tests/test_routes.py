from unittest.mock import Mock
from werkzeug.security import generate_password_hash
from app import create_app


def setup():
    store = Mock()
    user = {'id': 1, 'name': 'Student', 'role': 'student', 'password_hash': generate_password_hash('Password123')}
    store.get_user.side_effect = lambda uid: user if uid == 1 else None
    store.get_user_by_email.return_value = user
    store.search_alumni.return_value = []
    store.suggest_mentors.return_value = []
    store.list_requests.return_value = []
    app = create_app({'TESTING':True,'CSRF_ENABLED':False}, store=store)
    return app.test_client(),store


def test_auth():
    client,store = setup()
    assert client.get('/directory').status_code == 403
    assert client.post('/login',data={'email':'s@example.com','password':'bad'}).status_code == 200
    assert client.post('/login',data={'email':'s@example.com','password':'Password123'}).status_code == 302
    assert client.get('/directory').status_code == 200
    assert client.get('/profile').status_code == 403
    assert client.post('/logout').status_code == 302
    assert client.get('/requests').status_code == 403


def test_registration_validation():
    client,store = setup()
    client.post('/register',data={'name':'','email':'bad','password':'x','role':'student'})
    store.create_user.assert_not_called()
    assert client.post('/register',data={'name':'New','email':'new@example.com','password':'Password123','role':'student'}).status_code == 302
    assert store.create_user.call_args.args[2] != 'Password123'


def test_request_validation():
    client,store = setup()
    client.post('/login',data={'email':'s@example.com','password':'Password123'})
    client.post('/requests/new',data={'alumni_id':'2','message':''})
    store.create_request.assert_not_called()
    client.post('/requests/new',data={'alumni_id':'2','message':'Advice'})
    store.create_request.assert_called_once_with(1,2,'Advice')
    assert client.post('/requests/1/status',data={'status':'accepted'}).status_code == 403
