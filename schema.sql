CREATE TABLE IF NOT EXISTS users (
 id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('student','alumni'))
);
CREATE TABLE IF NOT EXISTS alumni_profiles (
 user_id INTEGER PRIMARY KEY REFERENCES users(id), industry TEXT NOT NULL,
 expertise TEXT NOT NULL, job_role TEXT NOT NULL, graduation_year INTEGER NOT NULL,
 consent INTEGER NOT NULL DEFAULT 0 CHECK(consent IN (0,1))
);
CREATE TABLE IF NOT EXISTS mentorship_requests (
 id INTEGER PRIMARY KEY, student_id INTEGER NOT NULL REFERENCES users(id),
 alumni_id INTEGER NOT NULL REFERENCES alumni_profiles(user_id), message TEXT NOT NULL,
 status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','accepted','rejected')),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE(student_id,alumni_id)
);
