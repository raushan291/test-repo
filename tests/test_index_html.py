import pytest
import os
import sys

# Adjust the path to import the Flask app from the directory containing app.py.
# Assuming tests are in a 'tests' subdirectory one level below the directory
# containing 'app.py' (e.g., project_root/app/app.py and project_root/app/tests/test_*.py).
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask app instance.
# 'app' refers to the app.py file, and 'app' as flask_app is the Flask object within it.
from app import app as flask_app

@pytest.fixture
def client():
    """
    Configures the Flask application for testing and provides a test client.
    This client allows simulating requests to the application without running a live server.
    """
    flask_app.config['TESTING'] = True  # Enable testing mode for Flask
    with flask_app.test_client() as client:
        yield client # Provide the client to the tests

def test_index_html_template_structure_and_content(client):
    """
    Tests that the index.html template renders with all the specified structural elements
    and correct content, including meta tags, title, headings, counter display,
    button, and static file links.
    """
    response = client.get('/')
    assert response.status_code == 200
    html_content = response.data.decode('utf-8')

    # 1. Document type and html tag with lang attribute
    assert '<!DOCTYPE html>' in html_content
    assert '<html lang="en">' in html_content

    # 2. Meta tags within <head>
    assert '<meta charset="UTF-8">' in html_content
    assert '<meta name="viewport" content="width=device-width, initial-scale=1.0">' in html_content

    # 3. Page title
    assert '<title>Simple Counter App</title>' in html_content

    # 4. Main heading <h1>
    assert '<h1>Counter Application</h1>' in html_content

    # 5. Counter display element: <span id="counter-value">0</span>
    # The app.py context resets 'current_count' to 0 on index load,
    # so 'initial_count' rendered in the template will be 0.
    assert '<span id="counter-value">0</span>' in html_content

    # 6. Increment button: <button id="increment-button">Increment Counter</button>
    assert '<button id="increment-button">Increment Counter</button>' in html_content

    # 7. Static file links correctly using Flask's url_for helper
    assert '<link rel="stylesheet" href="/static/style.css">' in html_content
    assert '<script src="/static/script.js"></script>' in html_content

    # Optional: Check for the container div for better structure
    assert '<div class="container">' in html_content
    assert '</div>' in html_content # Basic check for closing tag of the container