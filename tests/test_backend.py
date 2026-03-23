import pytest
from app import app, reset_counter_for_tests, get_counter

@pytest.fixture
def client():
    """
    Pytest fixture to configure the Flask app for testing and provide a test client.
    It ensures that the counter state is reset before and after each test to maintain
    test isolation and predictability.
    """
    app.config['TESTING'] = True  # Enable testing mode
    reset_counter_for_tests()    # Reset counter before the test starts
    with app.test_client() as client:
        yield client             # Provide the test client to the test function
    reset_counter_for_tests()    # Reset counter after the test finishes (teardown)

def test_initial_counter_value(client):
    """
    Tests that the '/api/counter' endpoint correctly returns the initial value (0)
    when accessed for the first time in a test session.
    """
    response = client.get('/api/counter')
    assert response.status_code == 200
    assert response.json == {'value': 0}

def test_increment_counter_once(client):
    """
    Tests the '/api/increment' endpoint to ensure it increments the counter by one
    and that the updated value is reflected in a subsequent call to '/api/counter'.
    """
    # Verify initial state
    initial_response = client.get('/api/counter')
    assert initial_response.json['value'] == 0

    # Perform increment
    increment_response = client.post('/api/increment')
    assert increment_response.status_code == 200
    assert increment_response.json['message'] == 'Counter incremented'
    assert increment_response.json['new_value'] == 1

    # Verify state after increment
    updated_response = client.get('/api/counter')
    assert updated_response.status_code == 200
    assert updated_response.json['value'] == 1

def test_multiple_increments(client):
    """
    Tests that the counter increments correctly after multiple consecutive POST requests
    to the '/api/increment' endpoint.
    """
    # Increment once
    client.post('/api/increment')
    response_1 = client.get('/api/counter')
    assert response_1.json['value'] == 1

    # Increment a second time
    client.post('/api/increment')
    response_2 = client.get('/api/counter')
    assert response_2.json['value'] == 2

    # Increment a third time
    client.post('/api/increment')
    response_3 = client.get('/api/counter')
    assert response_3.json['value'] == 3

def test_homepage_loads(client):
    """
    Tests that the root URL '/' successfully loads the main HTML page
    and contains key elements of the counter application.
    """
    response = client.get('/')
    assert response.status_code == 200
    # Check for specific HTML content to confirm the correct page is served
    assert b'<title>Counter App</title>' in response.data
    # The app renders initial_count (which is 0 after reset) directly into the div
    assert b'<div id="counter-display">0</div>' in response.data
    assert b'<button id="increment-button">Increment Counter</button>' in response.data
    assert b'<script src="/static/script.js"></script>' in response.data

def test_get_on_increment_endpoint_fails(client):
    """
    Tests an edge case: sending a GET request to an endpoint configured only for POST.
    Flask should return a 405 Method Not Allowed error.
    """
    response = client.get('/api/increment')
    assert response.status_code == 405 # HTTP 405 Method Not Allowed

def test_non_existent_api_endpoint(client):
    """
    Tests a failure case: accessing an API endpoint that does not exist.
    Flask should return a 404 Not Found error.
    """
    response = client.get('/api/nonexistent-endpoint')
    assert response.status_code == 404 # HTTP 404 Not Found