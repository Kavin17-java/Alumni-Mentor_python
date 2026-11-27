import os
from pathlib import Path
from werkzeug.security import generate_password_hash
from db import SQLiteStore


def seed():
    store = SQLiteStore(os.environ.get('DATABASE_PATH', str(Path(__file__).parent / 'instance' / 'alumni.db')))
    store.init_db()
    records = [('Demo Student','student@example.com','student'), ('Asha Kumar','asha@example.com','alumni'),
               ('Ravi Demo','ravi@example.com','alumni'), ('Private Demo','private@example.com','alumni')]
    for name,email,role in records:
        if store.get_user_by_email(email) is None:
            store.create_user(name,email,generate_password_hash('DemoPass123'),role)
    for email,industry,expertise,job,year,consent in [
        ('asha@example.com','Technology','Python, Web development','Software Engineer',2022,1),
        ('ravi@example.com','Finance','Data analysis, Excel','Analyst',2023,1),
        ('private@example.com','Technology','Python','Developer',2021,0)]:
        user = store.get_user_by_email(email)
        if store.get_profile(user['id']) is None:
            store.save_profile(user['id'],industry,expertise,job,year,consent)
    print('Fictional demo accounts ready. Password: DemoPass123')

if __name__ == '__main__':
    seed()
