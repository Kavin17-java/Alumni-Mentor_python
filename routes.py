from datetime import date
from flask import render_template, request, redirect, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash


def register_routes(app, store):
    def require_user(role=None):
        user = store.get_user(session.get('user_id'))
        if not user or (role and user['role'] != role):
            abort(403)
        return user

    @app.get('/')
    def home():
        return render_template('index.html')

    @app.route('/register', methods=['GET','POST'])
    def register():
        if request.method == 'POST':
            name = request.form.get('name','').strip()
            email = request.form.get('email','').strip().lower()
            password = request.form.get('password','')
            role = request.form.get('role','')
            try:
                if not name or len(name)>100 or '@' not in email or len(email)>254 or len(password)<8 or role not in ('student','alumni'):
                    raise ValueError('Enter valid details and a password of at least 8 characters.')
                store.create_user(name,email,generate_password_hash(password),role)
                flash('Account created. Please log in.')
                return redirect('/login')
            except ValueError as exc:
                flash(str(exc))
        return render_template('register.html')

    @app.route('/login', methods=['GET','POST'])
    def login():
        if request.method == 'POST':
            user = store.get_user_by_email(request.form.get('email',''))
            if user and check_password_hash(user['password_hash'],request.form.get('password','')):
                session.clear()
                session['user_id'] = user['id']
                return redirect('/profile' if user['role']=='alumni' else '/directory')
            flash('Invalid email or password.')
        return render_template('login.html')

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect('/')

    @app.get('/directory')
    def directory():
        require_user('student')
        filters = {k: request.args.get(k,'').strip() for k in ('industry','expertise','job_role','graduation_year','interest')}
        try:
            year = int(filters['graduation_year']) if filters['graduation_year'] else None
            if year is not None and not 1950<=year<=date.today().year:
                raise ValueError('Invalid graduation year.')
            alumni = store.search_alumni(filters['industry'],filters['expertise'],filters['job_role'],year)
            matches = store.suggest_mentors(filters['interest'])
        except ValueError:
            flash('Enter a valid graduation year.')
            alumni, matches = [], []
        return render_template('directory.html',alumni=alumni,matches=matches,filters=filters)

    @app.route('/profile', methods=['GET','POST'])
    def profile():
        user = require_user('alumni')
        if request.method == 'POST':
            try:
                industry, expertise, job = (request.form.get(k,'').strip() for k in ('industry','expertise','job_role'))
                year = int(request.form.get('graduation_year',''))
                if not all((industry,expertise,job)) or not 1950<=year<=date.today().year:
                    raise ValueError('Complete the profile with a valid graduation year.')
                store.save_profile(user['id'],industry,expertise,job,year,int(request.form.get('consent')=='1'))
                flash('Profile saved.')
                return redirect('/profile')
            except ValueError:
                flash('Complete the profile with valid details.')
        return render_template('profile.html',profile=store.get_profile(user['id']) or {})

    @app.post('/requests/new')
    def new_request():
        user = require_user('student')
        try:
            alumni_id = int(request.form.get('alumni_id',''))
            message = request.form.get('message','').strip()
            if not 1<=len(message)<=500:
                raise ValueError('Message must be 1–500 characters.')
            store.create_request(user['id'],alumni_id,message)
            flash('Mentoring request sent.')
        except ValueError as exc:
            flash('Could not send request: ' + str(exc))
        return redirect('/requests')

    @app.get('/requests')
    def requests_page():
        user = require_user()
        return render_template('requests.html',requests=store.list_requests(user['id']))

    @app.post('/requests/<int:request_id>/status')
    def status(request_id):
        user = require_user('alumni')
        try:
            store.update_request_status(request_id,user['id'],request.form.get('status',''))
            flash('Request updated.')
        except ValueError as exc:
            flash(str(exc))
        return redirect('/requests')

    @app.get('/reports')
    def reports():
        require_user()
        return render_template('reports.html',report=store.participation_report())

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    def error_page(error):
        return render_template('error.html',message=error.description),error.code
