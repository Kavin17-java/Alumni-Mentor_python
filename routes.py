# Temporary preview routes, replaced by Member 2's real routes.
from flask import render_template, request, redirect, flash

SAMPLE = {'id': 1, 'name': 'Asha Kumar', 'industry': 'Technology',
          'expertise': 'Python, Web development', 'job_role': 'Software Engineer',
          'graduation_year': 2022, 'consent': 1}


def register_routes(app, store):
    @app.get('/')
    def home():
        return render_template('index.html')

    @app.route('/register', methods=['GET', 'POST'])
    @app.route('/login', methods=['GET', 'POST'])
    @app.route('/profile', methods=['GET', 'POST'])
    def preview_form():
        if request.method == 'POST':
            flash('Preview only: backend not connected yet.')
        return render_template(request.path[1:] + '.html', profile=SAMPLE)

    @app.get('/directory')
    def directory():
        return render_template('directory.html', alumni=[SAMPLE], matches=[SAMPLE], filters={})

    @app.get('/requests')
    def requests_page():
        return render_template('requests.html', requests=[{'id': 1, 'student_name': 'Demo Student',
                               'alumni_name': SAMPLE['name'], 'message': 'Career guidance', 'status': 'pending'}])

    @app.get('/reports')
    def reports():
        return render_template('reports.html', report={'visible_alumni': 1, 'total_requests': 1,
                               'pending': 1, 'accepted': 0, 'rejected': 0})

    @app.post('/logout')
    @app.post('/requests/new')
    @app.post('/requests/<int:request_id>/status')
    def preview_action(request_id=None):
        flash('Preview only: backend not connected yet.')
        return redirect('/')

    @app.errorhandler(400)
    @app.errorhandler(403)
    @app.errorhandler(404)
    def error_page(error):
        return render_template('error.html', message=error.description), error.code
