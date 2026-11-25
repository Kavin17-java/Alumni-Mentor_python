import pytest
from db import SQLiteStore

@pytest.fixture
def sample(tmp_path):
    db = SQLiteStore(tmp_path / 'test.db')
    db.init_db()
    s = db.create_user('Student','s@example.com','hash','student')
    a = db.create_user('Alumni','a@example.com','hash','alumni')
    b = db.create_user('Private','b@example.com','hash','alumni')
    db.save_profile(a,'Tech','Python','Engineer',2022,1)
    db.save_profile(b,'Tech','Python','Engineer',2022,0)
    return db,s,a,b

def test_search(sample):
    db,s,a,b = sample
    assert [p['id'] for p in db.search_alumni('tech','python','engineer',2022)] == [a]
    assert db.search_alumni(graduation_year=2020) == []
    assert db.suggest_mentors('PYTHON')[0]['id'] == a
    assert db.suggest_mentors('') == []
    assert db.search_alumni(industry="' OR 1=1 --") == []

def test_invalid(sample):
    db,s,a,b = sample
    with pytest.raises(ValueError):
        db.create_user('Duplicate','S@example.com','hash','student')
    with pytest.raises(ValueError):
        db.save_profile(a,'Tech','Python','Engineer',1949,1)
    with pytest.raises(ValueError):
        db.create_request(s,b,'Hello')
    with pytest.raises(ValueError):
        db.create_request(a,a,'Hello')

def test_requests_reports(sample):
    db,s,a,b = sample
    assert db.participation_report()['total_requests'] == 0
    r = db.create_request(s,a,'Advice please')
    assert db.list_requests(b) == []
    with pytest.raises(ValueError):
        db.create_request(s,a,'Again')
    with pytest.raises(ValueError):
        db.update_request_status(r,b,'accepted')
    db.update_request_status(r,a,'accepted')
    assert db.list_requests(s)[0]['status'] == 'accepted'
    assert db.participation_report()['accepted'] == 1
    with pytest.raises(ValueError):
        db.update_request_status(r,a,'rejected')
    db.save_profile(a,'Tech','Python','Engineer',2022,0)
    assert db.search_alumni() == []
