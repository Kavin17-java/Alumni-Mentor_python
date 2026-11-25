# Shared contract

`app.py` creates the Flask app and injects a store into `register_routes(app, store)`. Database methods are defined below. Profiles and requests are dictionaries. Templates use `current_user` (id, name, role) and `csrf_token` from the app context.

- `init_db()`, `create_user(name,email,password_hash,role)`, `get_user(user_id)`, `get_user_by_email(email)`
- `save_profile(user_id,industry,expertise,job_role,graduation_year,consent)`, `get_profile(user_id)`
- `search_alumni(industry='',expertise='',job_role='',graduation_year=None)`, `suggest_mentors(interest)`
- `create_request(student_id,alumni_id,message)`, `list_requests(user_id)`, `update_request_status(request_id,alumni_id,status)`, `participation_report()`

Profile keys: id, name, industry, expertise, job_role, graduation_year, consent. Request keys: id, student_id, alumni_id, student_name, alumni_name, message, status, created_at. Report keys: visible_alumni, total_requests, pending, accepted, rejected.

URLs: /, /register (name,email,password,role), /login (email,password), /logout POST, /directory GET (industry,expertise,job_role,graduation_year,interest), /profile GET/POST (industry,expertise,job_role,graduation_year,consent), /requests GET, /requests/new POST (alumni_id,message), /requests/<id>/status POST (status), /reports GET. Every POST includes csrf_token.

Templates: index, register, login, directory (alumni,matches,filters), profile (profile), requests (requests), reports (report), error (message). All extend base.html. No real data until DB and backend are merged.
