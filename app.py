import os
import sys
from flask import Flask, render_template, request, jsonify

# Add the parent directory to the system path to allow importing modules like 'payments'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# Import our payment service and db mocks
from payments import payment_service, _reset_db, PaymentService

app = Flask(__name__)

# In-memory counter for the simple example
current_count = 0

# New counter reset specifically for tests that use the app client
def reset_counter_for_tests():
    """Resets the global counter and the payment service's mock database for testing."""
    global current_count
    current_count = 0
    _reset_db() # Reset payment service database for tests

@app.route('/')
def index():
    """
    Renders the main page of the counter application.
    Resets the counter on page load for a fresh start with each visit.
    """
    reset_counter_for_tests() # Ensure a fresh state for the UI
    return render_template('index.html', current_count=current_count)

@app.route('/increment', methods=['POST'])
def increment_counter():
    """
    Increments the global counter and returns the new value as JSON.
    Only accepts POST requests.
    """
    global current_count
    current_count += 1
    return jsonify({'count': current_count})

# API endpoints for the counter (used by test_backend.py)
@app.route('/api/counter', methods=['GET'])
def get_counter_api():
    """Returns the current counter value as JSON."""
    return jsonify({'value': current_count})

@app.route('/api/increment', methods=['POST'])
def increment_counter_api():
    """Increments the counter and returns a success message with the new value as JSON."""
    global current_count
    current_count += 1
    return jsonify({'message': 'Counter incremented', 'new_value': current_count})


# --- Payments Endpoints ---
@app.route('/api/payments/initiate', methods=['POST'])
def initiate_payment():
    """
    Endpoint to initiate a payment.
    Expects JSON payload with 'user_id', 'amount', and optional 'plan_id'.
    """
    data = request.get_json()
    user_id = data.get('user_id')
    amount = data.get('amount')
    plan_id = data.get('plan_id', 'basic')

    if not user_id or amount is None: # `amount` could be 0 which is handled by service
        return jsonify({"error": "User ID and amount are required."}), 400

    try:
        checkout_url, error = payment_service.initiate_payment(user_id, amount, plan_id)
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"checkout_url": checkout_url, "message": "Payment initiated successfully."}), 200
    except ValueError as e:
        # Catch validation errors from the payment service (e.g., negative amount)
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        # Catch any unexpected errors during initiation
        print(f"An unexpected error occurred during payment initiation: {e}")
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500

@app.route('/api/payments/webhook', methods=['POST'])
def handle_payment_webhook():
    """
    Endpoint for receiving payment gateway webhooks.
    Parses the webhook payload and delegates to the payment service.
    """
    # In a real application, you'd verify the webhook signature here
    # E.g., request.headers.get('Stripe-Signature')
    # For this exercise, we assume it's verified.

    payload = request.get_json()
    if not payload:
        return jsonify({"error": "Invalid JSON payload"}), 400

    event_type = payload.get('event_type')
    gateway_id = payload.get('gateway_id')
    payment_status = payload.get('status') # This is the status from the gateway, e.g., 'succeeded', 'failed'
    event_id = payload.get('event_id') # For idempotency, if the gateway provides one

    if not all([event_type, gateway_id, payment_status]):
        return jsonify({"error": "Missing event_type, gateway_id, or status in webhook payload"}), 400

    success, message = payment_service.handle_webhook(event_type, gateway_id, payment_status, event_id)

    # Webhook endpoints typically return 200 OK to acknowledge receipt,
    # even if internal processing had issues. The gateway just wants to know
    # you received it successfully. Specific error handling should be logged internally.
    if success:
        return jsonify({"message": message}), 200
    else:
        # Log the message if processing was unsuccessful internally
        print(f"Webhook processing failed for gateway_id {gateway_id}: {message}")
        return jsonify({"message": message, "status": "processed with issues"}), 200

@app.route('/api/payments/<payment_id>', methods=['GET'])
def get_payment_status_endpoint(payment_id):
    """
    Retrieves details for a specific payment by its internal ID.
    """
    payment = payment_service.get_payment_details(payment_id)
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    # In a production app, sanitize sensitive info before returning
    return jsonify(payment), 200

@app.route('/api/subscriptions/<user_id>', methods=['GET'])
def get_subscription_status_endpoint(user_id):
    """
    Retrieves the subscription status for a specific user.
    """
    subscription = payment_service.get_subscription_status(user_id)
    if not subscription:
        # If no subscription record, return a default inactive status
        return jsonify({"status": PaymentService.SUBSCRIPTION_INACTIVE, "message": "No active subscription found for this user."}), 200
    return jsonify(subscription), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)