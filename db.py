import sqlite3
from pathlib import Path
from contextlib import contextmanager
from datetime import date


class SQLiteStore:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        conn.execute('PRAGMA foreign_keys = ON')
        try:
            yield conn
            conn.commit()
        except sqlite3.IntegrityError as exc:
            conn.rollback()
            raise ValueError('Duplicate or invalid record.') from exc
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def init_db(self):
        schema = Path(__file__).with_name('schema.sql').read_text(encoding='utf-8')
        with self.connection() as conn:
            conn.executescript(schema)

    def create_user(self, name, email, password_hash, role):
        if not name.strip() or '@' not in email or not password_hash or role not in ('student', 'alumni'):
            raise ValueError('Invalid account details.')
        with self.connection() as conn:
            result = conn.execute('INSERT INTO users(name,email,password_hash,role) VALUES(?,?,?,?)',
                                  (name.strip(), email.strip().lower(), password_hash, role))
            return result.lastrowid

    def get_user(self, user_id):
        with self.connection() as conn:
            row = conn.execute('SELECT * FROM users WHERE id=?', (user_id,)).fetchone()
            return dict(row) if row else None

    def get_user_by_email(self, email):
        with self.connection() as conn:
            row = conn.execute('SELECT * FROM users WHERE email=?', (email.strip().lower(),)).fetchone()
            return dict(row) if row else None

    def save_profile(self, user_id, industry, expertise, job_role, graduation_year, consent):
        user = self.get_user(user_id)
        if not user or user['role'] != 'alumni':
            raise ValueError('Only alumni can create profiles.')
        if not all(v.strip() for v in (industry, expertise, job_role)) or not 1950 <= graduation_year <= date.today().year or consent not in (0, 1):
            raise ValueError('Invalid profile details.')
        with self.connection() as conn:
            conn.execute('''INSERT INTO alumni_profiles VALUES(?,?,?,?,?,?)
                ON CONFLICT(user_id) DO UPDATE SET industry=excluded.industry, expertise=excluded.expertise,
                job_role=excluded.job_role, graduation_year=excluded.graduation_year, consent=excluded.consent''',
                (user_id, industry.strip(), expertise.strip(), job_role.strip(), graduation_year, consent))

    def get_profile(self, user_id):
        with self.connection() as conn:
            row = conn.execute('SELECT u.id,u.name,p.industry,p.expertise,p.job_role,p.graduation_year,p.consent FROM alumni_profiles p JOIN users u ON u.id=p.user_id WHERE u.id=?', (user_id,)).fetchone()
            return dict(row) if row else None

    def search_alumni(self, industry='', expertise='', job_role='', graduation_year=None):
        sql = 'SELECT u.id,u.name,p.industry,p.expertise,p.job_role,p.graduation_year,p.consent FROM alumni_profiles p JOIN users u ON u.id=p.user_id WHERE p.consent=1'
        params = []
        for column, value in [('industry', industry), ('expertise', expertise), ('job_role', job_role)]:
            if value.strip():
                sql += ' AND instr(lower(p.' + column + '), lower(?)) > 0'
                params.append(value.strip())
        if graduation_year is not None:
            sql += ' AND p.graduation_year=?'
            params.append(graduation_year)
        with self.connection() as conn:
            return [dict(row) for row in conn.execute(sql + ' ORDER BY u.name,u.id', params)]

    def suggest_mentors(self, interest):
        return self.search_alumni(expertise=interest) if interest.strip() else []

    def create_request(self, student_id, alumni_id, message):
        student = self.get_user(student_id)
        profile = self.get_profile(alumni_id)
        if not student or student['role'] != 'student' or not profile or not profile['consent']:
            raise ValueError('Request not permitted.')
        if not 1 <= len(message.strip()) <= 500:
            raise ValueError('Message must contain 1 to 500 characters.')
        with self.connection() as conn:
            result = conn.execute('INSERT INTO mentorship_requests(student_id,alumni_id,message) VALUES(?,?,?)',
                                  (student_id, alumni_id, message.strip()))
            return result.lastrowid

    def list_requests(self, user_id):
        with self.connection() as conn:
            rows = conn.execute('''SELECT r.*,s.name AS student_name,a.name AS alumni_name
                FROM mentorship_requests r JOIN users s ON s.id=r.student_id JOIN users a ON a.id=r.alumni_id
                WHERE r.student_id=? OR r.alumni_id=? ORDER BY r.id DESC''', (user_id,user_id))
            return [dict(row) for row in rows]

    def update_request_status(self, request_id, alumni_id, status):
        if status not in ('accepted','rejected'):
            raise ValueError('Invalid status.')
        with self.connection() as conn:
            result = conn.execute("UPDATE mentorship_requests SET status=? WHERE id=? AND alumni_id=? AND status='pending'",
                                  (status, request_id, alumni_id))
            if result.rowcount != 1:
                raise ValueError('Request not found or cannot be updated.')

    def participation_report(self):
        with self.connection() as conn:
            report = {'visible_alumni': conn.execute('SELECT count(*) FROM alumni_profiles WHERE consent=1').fetchone()[0],
                      'total_requests': 0, 'pending': 0, 'accepted': 0, 'rejected': 0}
            for row in conn.execute('SELECT status,count(*) AS n FROM mentorship_requests GROUP BY status'):
                report[row['status']] = row['n']
                report['total_requests'] += row['n']
            return report
