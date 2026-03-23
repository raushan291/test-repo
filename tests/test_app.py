import pytest
from flask import Flask
import json
import os
import sys

# Add the parent directory to the system path to allow importing 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app as flask_app, current_count

@pytest.fixture
def client():
    """
    Configures the Flask application for testing and provides a test client.
    This client allows simulating requests to the application without running a live server.
    """
    flask_app.config['TESTING'] = True  # Enable testing mode for Flask
    with flask_app.test_client() as client:
        yield client # Provide the client to the tests

def test_index_page_loads_correctly(client):
    """
    Test that the root URL ('/') loads successfully and contains expected content.
    This verifies the HTML template rendering and basic content, including title,
    main heading, button text, and CSS link.
    """
    response = client.get('/')
    assert response.status_code == 200
    # Assertions updated to match index.html content and test_index.py expectations
    assert b"<title>Simple Counter App</title>" in response.data # Check for the page title
    assert b"<h1>Counter Application</h1>" in response.data # Check for the main heading
    assert b"Increment Counter" in response.data # Check for the increment button text
    assert b'<link rel="stylesheet" href="/static/style.css">' in response.data # Verify CSS link

def test_static_css_file_exists_and_is_served(client):
    """
    Test that the `style.css` file can be accessed via the `/static/` route,
    has the correct content type, and contains expected CSS rules, ensuring it's not empty.
    """
    response = client.get('/static/style.css')
    assert response.status_code == 200
    assert response.content_type == 'text/css; charset=utf-8' # Verify content type
    assert b"body {" in response.data # Check for a known CSS rule
    assert b"background-color: #f4f7f6;" in response.data # Check for specific rule
    assert len(response.data) > 100 # Ensure the file has substantial content

def test_increment_endpoint_increments_counter(client):
    """
    Test that the `/increment` endpoint correctly increments the global counter
    and returns the updated value.
    """
    # Reset the global counter to a known state before testing
    global current_count
    current_count = 0

    # First increment request
    response = client.post('/increment')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'count' in data
    assert data['count'] == 1 # Expected count after first increment
    assert current_count == 1 # Verify the global variable also updated

    # Second increment request
    response = client.post('/increment')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'count' in data
    assert data['count'] == 2 # Expected count after second increment
    assert current_count == 2

def test_counter_resets_on_index_load(client):
    """
    Test that the global counter resets to 0 when the index page is loaded.
    This ensures a fresh state for each new visit to the main page.
    """
    global current_count
    current_count = 5 # Set counter to a non-zero value

    # Access the index page, which should trigger a reset
    response = client.get('/')
    assert response.status_code == 200
    # Verify that the displayed count in the HTML is 0
    assert b'<div id="counter-display">0</div>' in response.data
    assert current_count == 0 # Verify the global variable itself has reset

    # Now, try incrementing again to ensure it starts from 0 after the reset
    response = client.post('/increment')
    data = json.loads(response.data)
    assert data['count'] == 1
    assert current_count == 1

def test_increment_method_restriction(client):
    """
    Test that the `/increment` endpoint only accepts POST requests.
    Attempts with other HTTP methods should result in a 405 Method Not Allowed error.
    """
    # Attempt to access with GET method
    response = client.get('/increment')
    assert response.status_code == 405 # GET is not allowed

    # Attempt to access with PUT method
    response = client.put('/increment')
    assert response.status_code == 405 # PUT is not allowed

    # Attempt to access with DELETE method
    response = client.delete('/increment')
    assert response.status_code == 405 # DELETE is not allowed

    # POST method should still work (sanity check)
    response = client.post('/increment')
    assert response.status_code == 200