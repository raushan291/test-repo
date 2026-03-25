import os

class Config:
    """
    Application configuration class.
    Loads settings from environment variables with sensible defaults for development.
    """
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-dev-key-please-change-in-prod'
    FLASK_ENV = os.environ.get('FLASK_ENV') or 'development'
    DEBUG = FLASK_ENV == 'development'

    # Stripe configuration (dummy values for local testing/development)
    # In a real app, these would be loaded securely from environment variables
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY') or 'sk_test_mock_secret_key_123'
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY') or 'pk_test_mock_publishable_key_abc'
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET') or 'whsec_mock_webhook_secret_xyz'

    # Base URL for redirects (e.g., for Stripe Checkout success/cancel URLs)
    BASE_URL = os.environ.get('BASE_URL') or 'http://localhost:5000'