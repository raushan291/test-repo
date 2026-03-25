# Payment Service Application

This application provides a simple payment and subscription management service, demonstrating how to initiate payments, handle webhooks, and query payment/subscription statuses. It uses Flask for the API and a mock payment gateway for testing purposes.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running Locally](#running-locally)
- [Running Tests](#running-tests)
- [API Endpoints](#api-endpoints)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before you begin, ensure you have the following software installed on your system:

*   **Python 3.8+**: This application is developed using Python. You can download it from [python.org](https://www.python.org/downloads/).
*   **pip**: Python's package installer. It usually comes bundled with Python installations.

## Installation

Follow these steps to set up and install the application locally:

1.  **Clone the Repository (if applicable)**:
    If you haven't already, clone the project repository to your local machine:
    git clone https://github.com/your-username/your-repo-name.git
    cd your-repo-name
    *(If you received the code in another way, skip this step and navigate to the project directory.)*

2.  **Create a Virtual Environment**:
    It's recommended to use a virtual environment to manage project dependencies.
    python3 -m venv venv

3.  **Activate the Virtual Environment**:
    *   **On macOS and Linux:**
        source venv/bin/activate
    *   **On Windows (Command Prompt):**
        venv\Scripts\activate.bat
    *   **On Windows (PowerShell):**
        venv\Scripts\Activate.ps1

4.  **Install Dependencies**:
    Install all required Python packages using pip:
    pip install -r requirements.txt

## Configuration

The application uses environment variables for sensitive data and dynamic settings. You need to set these variables before running the application.

Below are the key environment variables you might need to configure, along with their default development values (as seen in `config.py`):

*   `SECRET_KEY`: A strong, random key used by Flask for session management and other security-related functions.
    *   **Default (Development):** `'super-secret-dev-key-please-change-in-prod'`
    *   **Recommendation:** Generate a strong, random key for production.
*   `FLASK_ENV`: Sets the Flask environment (`development`, `production`, `testing`). Influences debugging behavior.
    *   **Default:** `'development'`
*   `STRIPE_SECRET_KEY`: Your Stripe secret key for making API calls.
    *   **Default (Development):** `'sk_test_mock_secret_key_123'` (mock value)
    *   **Recommendation:** Use your actual Stripe secret key for real transactions.
*   `STRIPE_PUBLISHABLE_KEY`: Your Stripe publishable key for client-side use.
    *   **Default (Development):** `'pk_test_mock_publishable_key_abc'` (mock value)
*   `STRIPE_WEBHOOK_SECRET`: A secret used to verify Stripe webhook signatures.
    *   **Default (Development):** `'whsec_mock_webhook_secret_xyz'` (mock value)
*   `BASE_URL`: The base URL of your application, used for constructing redirect URLs (e.g., Stripe Checkout success/cancel).
    *   **Default:** `'http://localhost:5000'`

**How to set environment variables:**

*   **On macOS and Linux (for the current session):**
    export SECRET_KEY="your_super_secret_key"
    export STRIPE_SECRET_KEY="your_real_stripe_secret_key"
    export STRIPE_PUBLISHABLE_KEY="your_real_stripe_publishable_key"
    export STRIPE_WEBHOOK_SECRET="your_real_stripe_webhook_secret"
    export BASE_URL="http://localhost:5000"
    export FLASK_ENV="development" # Or "production" for production deployment
*   **On Windows (Command Prompt, for the current session):**
    set SECRET_KEY="your_super_secret_key"
    set STRIPE_SECRET_KEY="your_real_stripe_secret_key"
    set STRIPE_PUBLISHABLE_KEY="your_real_stripe_publishable_key"
    set STRIPE_WEBHOOK_SECRET="your_real_stripe_webhook_secret"
    set BASE_URL="http://localhost:5000"
    set FLASK_ENV="development"
*   **On Windows (PowerShell, for the current session):**
    $env:SECRET_KEY="your_super_secret_key"
    $env:STRIPE_SECRET_KEY="your_real_stripe_secret_key"
    $env:STRIPE_PUBLISHABLE_KEY="your_real_stripe_publishable_key"
    $env:STRIPE_WEBHOOK_SECRET="your_real_stripe_webhook_secret"
    $env:BASE_URL="http://localhost:5000"
    $env:FLASK_ENV="development"
*   **Using a `.env` file (recommended for local development):**
    You can create a `.env` file in the root of your project and store your environment variables there. Many tools (like `python-dotenv`) can load these automatically.
    SECRET_KEY="your_super_secret_key"
    STRIPE_SECRET_KEY="your_real_stripe_secret_key"
    STRIPE_PUBLISHABLE_KEY="your_real_stripe_publishable_key"
    STRIPE_WEBHOOK_SECRET="your_real_stripe_webhook_secret"
    BASE_URL="http://localhost:5000"
    FLASK_ENV="development"
    To use `.env` files, you would typically `pip install python-dotenv` and then load them in your `app.py` before `app.config.from_object(Config)`. For simplicity, this project directly uses `os.environ.get()`, so setting them in your shell is the direct way.

## Running Locally

Once installed and configured, you can run the application:

1.  **Activate your virtual environment** (if not already active):
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate.bat` or `venv\Scripts\Activate.ps1`

2.  **Set Flask App and Environment (if not using .env file)**:
    export FLASK_APP=app.py
    export FLASK_ENV=development # Ensure debug mode is on for development
    (Use `set` instead of `export` for Windows Command Prompt, and `$env:` for PowerShell)

3.  **Start the Flask Development Server**:
    flask run
    The application should now be running on `http://localhost:5000`.

## Running Tests

The project includes a suite of tests using `pytest` to ensure functionality.

1.  **Activate your virtual environment**:
    `source venv/bin/activate` (or your OS equivalent)

2.  **Navigate to the project root directory**.

3.  **Run Pytest**:
    pytest
    This will discover and run all test files (e.g., `test_payments.py`) in the `tests/` directory.

## API Endpoints

The application exposes the following REST API endpoints:

*   **`POST /api/payments/initiate`**
    *   Initiates a new payment process.
    *   **Request Body:** `{"user_id": "string", "amount": float, "plan_id": "string" (optional, default "basic")}`
    *   **Success Response:** `{"message": "Payment initiated successfully.", "checkout_url": "string"}`
    *   **Error Response:** `{"error": "string"}`

*   **`POST /api/payments/webhook`**
    *   Endpoint for receiving payment gateway webhooks to update payment and subscription statuses.
    *   **Request Body:** `{"event_type": "string", "gateway_id": "string", "status": "string", "event_id": "string" (optional)}`
    *   **Success Response (for handled events):** `{"message": "string"}` (e.g., "Payment succeeded and subscription activated.")
    *   **Error Response (for malformed requests):** `{"error": "string"}` (though typically returns 200 with informative message for handled events, even if an internal issue occurs)

*   **`GET /api/payments/<payment_id>`**
    *   Retrieves details for a specific payment.
    *   **Success Response:** `{"payment_id": "string", "user_id": "string", "amount": float, "plan_id": "string", "status": "string", "gateway_id": "string", "checkout_url": "string", "error": null, "created_at": "datetime_string", "updated_at": "datetime_string"}`
    *   **Error Response:** `{"error": "Payment not found"}` (404 Not Found)

*   **`GET /api/subscriptions/<user_id>`**
    *   Retrieves the subscription status for a specific user.
    *   **Success Response (active):** `{"user_id": "string", "status": "ACTIVE", "plan_id": "string", "starts_at": "datetime_string", "expires_at": "datetime_string", "payment_id": "string", "updated_at": "datetime_string"}`
    *   **Success Response (inactive):** `{"status": "INACTIVE", "message": "No active subscription found for this user."}`

## Troubleshooting

Here are some common issues and their solutions:

*   **`python3: command not found` or `python: command not found`**:
    *   **Solution:** Ensure Python is installed and correctly added to your system's PATH. You might need to use `python` instead of `python3` depending on your installation, or vice-versa.

*   **`pip: command not found`**:
    *   **Solution:** `pip` usually comes with Python. If not, you might need to reinstall Python or install `pip` separately. Ensure Python's `Scripts` directory (on Windows) or `/usr/local/bin` (on Linux/macOS) is in your PATH.

*   **`ModuleNotFoundError: No module named 'flask'` (or any other module)**:
    *   **Solution:**
        1.  Ensure your virtual environment is activated.
        2.  Run `pip install -r requirements.txt` to install all dependencies.
        3.  If still an issue, try `pip install Flask` (or the missing module explicitly).

*   **`Address already in use` when running `flask run`**:
    *   **Solution:** Another process is already using port 5000.
        *   Find and terminate the process using that port (e.g., `lsof -i :5000` on macOS/Linux, `netstat -ano | findstr :5000` on Windows, then `taskkill /PID <PID> /F`).
        *   Alternatively, run Flask on a different port: `flask run --port 5001`.

*   **Environment variables not being recognized**:
    *   **Solution:**
        1.  Verify that you've set the environment variables correctly for your operating system and shell.
        2.  Make sure they are set *before* you run `flask run`. For example, `export VAR=value && flask run`.
        3.  If using a `.env` file, ensure `python-dotenv` is installed and loaded in `app.py`.

*   **Tests are failing unexpectedly**:
    *   **Solution:**
        1.  Ensure your virtual environment is active and all dependencies (including `pytest`) are installed.
        2.  Check the test output for specific error messages.
        3.  The mock database is reset before each test, so tests should be isolated. If state is leaking, investigate test fixtures or global state.

---