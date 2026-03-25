from flask import Flask, request, jsonify
from payments import payment_service, _reset_db # Import the global instance and reset function
from config import Config
import os
import datetime

app = Flask(__name__)
app.config.from_object(Config)

# Counter for a hypothetical feature, mentioned in test_payments.py fixture
_counter = 0

def reset_counter_for_tests():
    """
    Resets application-level counter and the mock payment/subscription databases.
    Used for test isolation.
    """
    global _counter
    _counter = 0
    _reset_db() # Also reset the payments DB as per test_payments.py fixture

@app.route('/')
def hello_world():
    global _counter
    _counter += 1
    return f'Hello, World! Counter: {_counter}'

# API Endpoints for payments
@app.route('/api/payments/initiate', methods=['POST'])
def initiate_payment():
    """
    Initiates a new payment process.
    Expected JSON: {"user_id": "string", "amount": float, "plan_id": "string"}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400
    user_id = data.get('user_id')
    amount = data.get('amount')
    plan_id = data.get('plan_id', 'basic')

    if not user_id: # Amount validation is largely handled by payment_service itself
        return jsonify({"error": "User ID and amount are required."}), 400
    if not isinstance(amount, (int, float)):
        return jsonify({"error": "Amount must be a number."}), 400

    checkout_url, error = payment_service.initiate_payment(user_id, amount, plan_id)

    if error:
        # PaymentService's initiate_payment returns specific error strings, including amount validation
        return jsonify({"error": error}), 400
    return jsonify({"message": "Payment initiated successfully.", "checkout_url": checkout_url}), 200

@app.route('/api/payments/webhook', methods=['POST'])
def handle_payment_webhook():
    """
    Endpoint for receiving payment gateway webhooks.
    Expected JSON: {"event_type": "string", "gateway_id": "string", "status": "string", "event_id": "string"}
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid JSON payload"}), 400

    event_type = data.get('event_type')
    gateway_id = data.get('gateway_id')
    status = data.get('status')
    event_id = data.get('event_id') # event_id is mentioned in tests but not used in payments.handle_webhook signature

    if not all([event_type, gateway_id, status]):
        return jsonify({"error": "Missing event_type, gateway_id, or status"}), 400
    
    success, message = payment_service.handle_webhook(event_type, gateway_id, status, event_id)

    # For webhooks, typically return 200 OK even for internal processing errors
    # to avoid repeated delivery from the gateway. The message contains the actual status.
    return jsonify({"message": message}), 200

@app.route('/api/payments/<string:payment_id>', methods=['GET'])
def get_payment_details(payment_id):
    """
    Retrieves details for a specific payment by its internal ID.
    """
    payment = payment_service.get_payment_details(payment_id)
    if payment:
        # Convert datetime objects to string for JSON serialization
        payment_copy = payment.copy()
        for key in ['created_at', 'updated_at']:
            if key in payment_copy and payment_copy[key]:
                payment_copy[key] = payment_copy[key].isoformat()
        return jsonify(payment_copy), 200
    return jsonify({"error": "Payment not found"}), 404

@app.route('/api/subscriptions/<string:user_id>', methods=['GET'])
def get_subscription_status(user_id):
    """
    Retrieves the subscription status for a specific user.
    """
    subscription = payment_service.get_subscription_status(user_id)
    if subscription:
        # Convert datetime objects to string for JSON serialization
        sub_copy = subscription.copy()
        for key in ['starts_at', 'expires_at', 'updated_at']:
            if key in sub_copy and sub_copy[key]:
                sub_copy[key] = sub_copy[key].isoformat()
        return jsonify(sub_copy), 200
    # If no subscription record, return INACTIVE status with informative message
    return jsonify({"status": payment_service.SUBSCRIPTION_INACTIVE, "message": "No active subscription found for this user."}), 200

if __name__ == '__main__':
    # When running directly, ensure FLASK_APP is set (e.g., via environment or directly here)
    # app.run() picks up FLASK_ENV from environment, defaults to production if not set.
    # For local development, set FLASK_ENV=development in your shell before running, or
    # explicitly set debug=True here:
    app.run(debug=app.config['DEBUG'])