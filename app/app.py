import os
from flask import Flask, render_template, request, jsonify

# Global variable to store the counter value
current_count = 0

# Initialize Flask app
# Specify template_folder and static_folder relative to the app.py file
# This setup assumes app.py is in 'app/' directory and
# templates are in 'app/templates/' and static files in 'app/static/'
app = Flask(__name__,
            template_folder='templates',
            static_folder='static',
            static_url_path='/static') # Explicitly set static_url_path for clarity

@app.route('/')
def index():
    """
    Renders the main index page.
    Resets the counter to 0 upon loading the homepage, as per requirements.
    The initial_count is passed to the template for display.
    """
    global current_count
    current_count = 0 # Reset counter to 0 when the index page is loaded
    return render_template('index.html', initial_count=current_count)

@app.route('/increment', methods=['POST'])
def increment_counter():
    """
    Increments the global counter and returns the updated value as JSON.
    This endpoint only accepts POST requests.
    """
    global current_count
    current_count += 1
    return jsonify({'count': current_count})

if __name__ == '__main__':
    # This block is for local development purposes only.
    # In a production environment, a WSGI server (e.g., Gunicorn, uWSGI)
    # would be used to serve the Flask application.
    app.run(debug=True, host='0.0.0.0', port=5000)