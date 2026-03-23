from flask import Flask, render_template, send_from_directory, jsonify
import os

# Initialize the Flask application
app = Flask(__name__)

# A global counter variable managed for demonstration purposes.
# This is explicitly made global for testability and application state management.
current_count = 0

# Utility functions for testing and application state inspection
def get_counter():
    """
    Returns the current value of the global counter.
    This function is primarily for test suites to inspect the application's state.
    """
    return current_count

def reset_counter_for_tests():
    """
    Resets the global counter to 0.
    This function is critical for test isolation, ensuring each test starts with
    a predictable counter state.
    """
    global current_count
    current_count = 0

@app.route('/')
def index():
    """
    Serves the main HTML page for the counter application.
    Resets the global counter to 0 upon each visit to the index page for demo consistency.
    """
    # The existing behavior for the app is to reset the counter on index load.
    # This behavior is maintained as per original application logic.
    reset_counter_for_tests()
    # Pass the current (reset) counter value to the template for initial display.
    return render_template('index.html', initial_count=get_counter())

@app.route('/api/counter')
def get_counter_api():
    """
    Returns the current value of the global counter as a JSON response.
    This endpoint is designed for API clients to fetch the counter's state.
    """
    return jsonify({'value': get_counter()})

@app.route('/api/increment', methods=['POST'])
def increment():
    """
    Increments the global counter by one and returns the new value as a JSON response.
    This endpoint only accepts POST requests.
    """
    global current_count
    current_count += 1
    # Return the updated count as a JSON object, adhering to test expectations.
    return jsonify({'message': 'Counter incremented', 'new_value': current_count})

@app.route('/static/<path:filename>')
def static_files(filename):
    """
    Serves static files (like CSS, JavaScript, images) from the 'static' directory.
    This route handles requests for resources like '/static/style.css'.
    """
    # Ensure the static directory exists relative to the current file
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    return send_from_directory(static_dir, filename)

if __name__ == '__main__':
    # This block allows the Flask application to be run directly using `python app.py`.
    # `debug=True` enables the debugger and auto-reloader for development.
    # For production deployment, a WSGI server (e.g., Gunicorn, uWSGI) should be used.
    app.run(debug=True, port=5000)