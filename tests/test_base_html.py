import pytest
from flask import Flask, render_template, session, Blueprint, url_for
from bs4 import BeautifulSoup
import os

# Define a temporary path for the base.html template for testing
TEST_TEMPLATE_PATH = 'tests/temp_base.html'

# Content of the modified base.html for testing purposes
# This mirrors the content provided in the solution
BASE_HTML_CONTENT = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Flask App{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <header>
        <nav class="navbar">
            <div class="navbar-brand">
                <a href="{{ url_for('index') }}">My App</a>
            </div>
            <ul class="navbar-nav">
                {% if session.get('logged_in') %}
                    <li><a href="{{ url_for('dashboard.index') }}">Dashboard</a></li>
                    <li><a href="{{ url_for('dashboard.settings') }}">Settings</a></li>
                    {# Navigation link to the profile page, visible only to authenticated users #}
                    <li><a href="{{ url_for('dashboard.profile') }}">Profile</a></li>
                    <li><span>Hello, {{ session.get('username', 'Guest') }}</span></li>
                    <li><a href="{{ url_for('auth.logout') }}">Logout</a></li>
                {% else %}
                    <li><a href="{{ url_for('auth.login') }}">Login</a></li>
                    <li><a href="{{ url_for('auth.register') }}">Register</a></li>
                {% endif %}
            </ul>
        </nav>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                <div class="flashes">
                    {% for category, message in messages %}
                        <p class="flash-{{ category }}">{{ message }}</p>
                    {% endfor %}
                </div>
            {% endif %}
        {% endwith %}
    </header>

    <main>
        {% block content %}{% endblock %}
    </main>

    <footer>
        <p>&copy; 2023 Flask App</p>
    </footer>

    <script src="{{ url_for('static', filename='js/script.js') }}"></script>
</body>
</html>
"""

@pytest.fixture
def app():
    """
    Sets up a minimal Flask application for testing the base.html template.
    It includes mock blueprints and routes to allow url_for to function,
    and handles session management for conditional rendering checks.
    """
    app = Flask(__name__, template_folder=os.path.dirname(TEST_TEMPLATE_PATH))
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'a_very_secret_key_for_testing_session'

    # Create dummy blueprints
    dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')
    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

    # Dummy routes required for url_for in base.html
    @app.route('/')
    def index():
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    @dashboard_bp.route('/')
    def dashboard_index():
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    @dashboard_bp.route('/settings')
    def dashboard_settings():
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    @dashboard_bp.route('/profile')
    def dashboard_profile():
        """
        The new /profile route. This is defined here to make url_for('dashboard.profile')
        resolvable during tests.
        """
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    @auth_bp.route('/login')
    def auth_login():
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    @auth_bp.route('/register')
    def auth_register():
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    @auth_bp.route('/logout')
    def auth_logout():
        session.pop('logged_in', None)
        session.pop('username', None)
        return render_template(os.path.basename(TEST_TEMPLATE_PATH))

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(auth_bp)

    # Ensure the directory for the temporary template exists
    os.makedirs(os.path.dirname(TEST_TEMPLATE_PATH), exist_ok=True)
    # Write the base.html content to a temporary file for the test
    with open(TEST_TEMPLATE_PATH, 'w') as f:
        f.write(BASE_HTML_CONTENT)

    yield app

    # Clean up the temporary template file after tests
    os.remove(TEST_TEMPLATE_PATH)


@pytest.fixture
def client(app):
    """Provides a test client for the Flask app."""
    return app.test_client()


def test_profile_link_not_visible_when_logged_out(client, app):
    """
    Verifies that the 'Profile' link is not rendered when the user is not authenticated.
    """
    with client:
        # Ensure the session is not logged in before making the request
        with app.test_request_context():
            if session.get('logged_in'):
                session.pop('logged_in')
            if session.get('username'):
                session.pop('username')

        response = client.get('/')
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Assert that the Profile link is NOT present
        profile_link = soup.find('a', string='Profile')
        assert profile_link is None, "Profile link should not be visible when logged out."

        # Assert that login/register links ARE present
        login_link = soup.find('a', string='Login')
        assert login_link is not None, "Login link should be visible when logged out."
        with app.test_request_context():
            assert login_link['href'] == url_for('auth.login')

        register_link = soup.find('a', string='Register')
        assert register_link is not None, "Register link should be visible when logged out."
        with app.test_request_context():
            assert register_link['href'] == url_for('auth.register')


def test_profile_link_visible_when_logged_in(client, app):
    """
    Verifies that the 'Profile' link is rendered with the correct href
    when the user is authenticated.
    """
    with client:
        # Simulate a logged-in session
        with client.session_transaction() as sess:
            sess['logged_in'] = True
            sess['username'] = 'testuser'

        response = client.get('/')
        assert response.status_code == 200
        soup = BeautifulSoup(response.data, 'html.parser')

        # Assert that the Profile link IS present
        profile_link = soup.find('a', string='Profile')
        assert profile_link is not None, "Profile link should be visible when logged in."

        # Verify the href attribute of the profile link
        with app.test_request_context():
            expected_profile_href = url_for('dashboard.profile')
        assert profile_link['href'] == expected_profile_href, \
            f"Profile link href mismatch. Expected '{expected_profile_href}', got '{profile_link['href']}'."

        # Assert that other authenticated links ARE present
        dashboard_link = soup.find('a', string='Dashboard')
        assert dashboard_link is not None
        with app.test_request_context():
            assert dashboard_link['href'] == url_for('dashboard.index')

        settings_link = soup.find('a', string='Settings')
        assert settings_link is not None
        with app.test_request_context():
            assert settings_link['href'] == url_for('dashboard.settings')

        logout_link = soup.find('a', string='Logout')
        assert logout_link is not None
        with app.test_request_context():
            assert logout_link['href'] == url_for('auth.logout')

        # Assert that login/register links are NOT present
        login_link = soup.find('a', string='Login')
        assert login_link is None, "Login link should not be visible when logged in."

        register_link = soup.find('a', string='Register')
        assert register_link is None, "Register link should not be visible when logged in."