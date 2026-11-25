import os
import secrets
from pathlib import Path
from flask import Flask, session, request, abort
from db import SQLiteStore
from routes import register_routes


def create_app(config=None, store=None):
    app = Flask(__name__)
    app.config.update(SECRET_KEY=os.environ.get('SECRET_KEY') or secrets.token_hex(32),
                      DATABASE_PATH=os.environ.get('DATABASE_PATH', str(Path(app.instance_path) / 'alumni.db')),
                      CSRF_ENABLED=True)
    if config:
        app.config.update(config)
    if store is None:
        store = SQLiteStore(app.config['DATABASE_PATH'])
    store.init_db()

    @app.context_processor
    def common_context():
        if 'csrf_token' not in session:
            session['csrf_token'] = secrets.token_hex(24)
        user = store.get_user(session.get('user_id')) if session.get('user_id') else None
        safe_user = {k: user[k] for k in ('id', 'name', 'role')} if user else None
        return {'csrf_token': session['csrf_token'], 'current_user': safe_user}

    @app.before_request
    def verify_csrf():
        if request.method == 'POST' and app.config['CSRF_ENABLED']:
            token = session.get('csrf_token', '')
            if not token or not secrets.compare_digest(token, request.form.get('csrf_token', '')):
                abort(400)

    register_routes(app, store)
    return app


app = create_app()
if __name__ == '__main__':
    app.run()
