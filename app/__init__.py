from flask import Flask, session, redirect, url_for, flash

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'a_very_secret_key_for_testing'
    app.template_folder = 'templates' # Explicitly set template folder for clarity

    # Import and register blueprints
    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.payments import payments_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(payments_bp, url_prefix='/payments')

    # Basic root route
    @app.route('/')
    def index():
        return "Welcome to the dummy Flask app! Navigate to /dashboard/profile, /auth/login, etc."

    return app