import pytest
from flask import json
from unittest.mock import patch, MagicMock
import os
import sys
import uuid
import datetime

# Add the parent directory to the system path to allow importing 'app' and 'payments'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the Flask app, its test reset function, and the payment service components
from app import app as flask_app, reset_counter_for_tests
from payments import _db_payments, _db_subscriptions, PaymentService, MockPaymentGateway, _reset_db

@pytest.fixture
def client():
    """
    Configures the Flask application for testing and provides a test client.
    Resets both the counter (from app.py) and the payments/subscriptions databases
    (via reset_counter_for_tests in app.py).
    """
    flask_app.config['TESTING'] = True
    reset_counter_for_tests() # Resets app counter and payment DBs before test
    with flask_app.test_client() as client:
        yield client # Provide the test client to the test function
    reset_counter_for_tests() # Teardown: Reset again after test finishes

@pytest.fixture
def mock_gateway():
    """
    Fixture to provide a mock PaymentGateway instance for tests.
    It patches the `MockPaymentGateway` class within the `payments` module
    to control its behavior during tests.
    """
    with patch('payments.MockPaymentGateway', autospec=True) as mock_class:
        mock_instance = mock_class.return_value
        # Default behavior for create_charge can be overridden in tests
        mock_instance.create_charge.return_value = {
            "status": "pending",
            "gateway_id": "mock_gateway_id_" + str(uuid.uuid4()),
            "checkout_url": "https://mock-gateway.com/checkout/mock_id",
            "error": None
        }
        yield mock_instance

@pytest.fixture(autouse=True)
def clear_db():
    """
    An autouse fixture to ensure the mock database is cleared before and after each test.
    This ensures test isolation.
    """
    _reset_db()
    yield
    _reset_db()

# --- Helper function for tests ---
def _create_pending_payment(user_id, amount, plan_id="basic", gateway_id=None):
    """
    Helper function to directly create a pending payment in the mock database.
    Useful for setting up specific test scenarios, especially for webhooks.
    Returns the internal payment_id and the gateway_id.
    """
    payment_id = str(uuid.uuid4())
    gw_id = gateway_id if gateway_id else "gw_" + str(uuid.uuid4())
    created_at = datetime.datetime.now(datetime.timezone.utc)
    _db_payments[payment_id] = {
        "payment_id": payment_id,
        "user_id": user_id,
        "amount": amount,
        "plan_id": plan_id,
        "status": PaymentService.STATUS_PENDING,
        "gateway_id": gw_id,
        "checkout_url": f"https://mock-gateway.com/checkout/{gw_id}",
        "error": None,
        "created_at": created_at,
        "updated_at": created_at,
    }
    return payment_id, gw_id


# --- Test Payment Initiation ---

def test_initiate_payment_success(client, mock_gateway):
    """
    Tests successful payment initiation through the API endpoint.
    Verifies the Flask response and the corresponding payment record
    in the mock database.
    """
    user_id = "test_user_123"
    amount = 99.99
    plan_id = "premium"

    response = client.post(
        '/api/payments/initiate',
        json={'user_id': user_id, 'amount': amount, 'plan_id': plan_id}
    )

    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'checkout_url' in data
    assert 'message' in data
    assert data['message'] == "Payment initiated successfully."

    # Verify payment record in mock DB
    assert len(_db_payments) == 1
    payment_record = list(_db_payments.values())[0]
    assert payment_record['user_id'] == user_id
    assert payment_record['amount'] == amount
    assert payment_record['plan_id'] == plan_id
    assert payment_record['status'] == PaymentService.STATUS_PENDING
    assert payment_record['gateway_id'] is not None
    assert payment_record['checkout_url'] == data['checkout_url']
    mock_gateway.create_charge.assert_called_once_with(amount, user_id)

def test_initiate_payment_missing_fields(client):
    """
    Tests payment initiation with missing required fields (user_id, amount).
    Ensures appropriate error responses.
    """
    # Missing amount
    response = client.post('/api/payments/initiate', json={'user_id': 'user1'})
    assert response.status_code == 400
    assert "error" in json.loads(response.data)
    assert "amount are required" in json.loads(response.data)['error']

    # Missing user_id
    response = client.post('/api/payments/initiate', json={'amount': 100})
    assert response.status_code == 400
    assert "error" in json.loads(response.data)
    assert "User ID and amount are required" in json.loads(response.data)['error']

def test_initiate_payment_invalid_amount(client, mock_gateway):
    """
    Tests payment initiation with an invalid amount (zero or negative).
    Ensures validation occurs before calling the gateway and a failure record is created.
    """
    user_id = "test_user_invalid_amount"
    
    # Zero amount
    response = client.post('/api/payments/initiate', json={'user_id': user_id, 'amount': 0})
    assert response.status_code == 400
    assert "Amount must be a positive number" in json.loads(response.data)['error']
    assert len(_db_payments) == 1 # A record should still be made with INITIATION_FAILED status
    assert list(_db_payments.values())[0]['status'] == PaymentService.STATUS_INITIATION_FAILED
    mock_gateway.create_charge.assert_not_called() # Gateway should not be called for invalid input

    _reset_db() # Clear for next assertion

    # Negative amount
    response = client.post('/api/payments/initiate', json={'user_id': user_id, 'amount': -10})
    assert response.status_code == 400
    assert "Amount must be a positive number" in json.loads(response.data)['error']
    assert len(_db_payments) == 1
    assert list(_db_payments.values())[0]['status'] == PaymentService.STATUS_INITIATION_FAILED
    mock_gateway.create_charge.assert_not_called()

def test_initiate_payment_gateway_rejects_transaction(client, mock_gateway):
    """
    Tests scenario where the mock payment gateway rejects the transaction immediately
    during the `create_charge` call.
    Verifies the error response and that the payment record reflects initiation failure.
    """
    user_id = "gateway_fail_user"
    amount = 123.45 # Any valid amount for this test, as mock_gateway behavior is patched

    # Configure the mock gateway to return a failed status
    mock_gateway.create_charge.return_value = {
        "status": "failed",
        "gateway_id": None,
        "checkout_url": None,
        "error": "Gateway rejected transaction: insufficient funds"
    }

    response = client.post(
        '/api/payments/initiate',
        json={'user_id': user_id, 'amount': amount}
    )

    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Gateway rejected transaction" in data['error']

    # Verify payment record in mock DB
    assert len(_db_payments) == 1
    payment_record = list(_db_payments.values())[0]
    assert payment_record['user_id'] == user_id
    assert payment_record['amount'] == amount
    assert payment_record['status'] == PaymentService.STATUS_INITIATION_FAILED
    assert payment_record['gateway_id'] is None
    assert payment_record['checkout_url'] is None
    assert "insufficient funds" in payment_record['error']
    mock_gateway.create_charge.assert_called_once_with(amount, user_id)

# --- Test Webhook Processing ---

def test_webhook_payment_succeeded(client):
    """
    Tests processing a 'payment.succeeded' webhook.
    Verifies that the payment status is updated to COMPLETED and
    a new subscription record is created and set to ACTIVE.
    """
    user_id = "webhook_success_user"
    amount = 50.00
    plan_id = "pro"
    payment_id, gateway_id = _create_pending_payment(user_id, amount, plan_id)
    event_id = str(uuid.uuid4())

    payload = {
        "event_type": "payment.succeeded",
        "gateway_id": gateway_id,
        "status": "succeeded", # Gateway's status representation
        "event_id": event_id
    }

    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Payment succeeded and subscription activated."

    # Verify payment status in our mock DB
    updated_payment = _db_payments[payment_id]
    assert updated_payment['status'] == PaymentService.STATUS_COMPLETED

    # Verify subscription status in our mock DB
    subscription = _db_subscriptions.get(user_id)
    assert subscription is not None
    assert subscription['status'] == PaymentService.SUBSCRIPTION_ACTIVE
    assert subscription['plan_id'] == plan_id
    assert subscription['payment_id'] == payment_id
    assert subscription['starts_at'] is not None
    assert subscription['expires_at'] is not None
    assert subscription['expires_at'] > subscription['starts_at']

def test_webhook_payment_failed(client):
    """
    Tests processing a 'payment.failed' webhook.
    Verifies that the payment status is updated to FAILED and
    any existing subscription for the user is set to INACTIVE.
    """
    user_id = "webhook_fail_user"
    amount = 25.00
    payment_id, gateway_id = _create_pending_payment(user_id, amount)
    event_id = str(uuid.uuid4())

    # Simulate an active subscription before failure (e.g., for a renewal that failed)
    _db_subscriptions[user_id] = {
        "user_id": user_id,
        "status": PaymentService.SUBSCRIPTION_ACTIVE,
        "plan_id": "basic",
        "starts_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10),
        "expires_at": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=20),
        "payment_id": payment_id,
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }

    payload = {
        "event_type": "payment.failed",
        "gateway_id": gateway_id,
        "status": "failed",
        "event_id": event_id
    }

    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Payment failed and subscription deactivated."

    # Verify payment status
    updated_payment = _db_payments[payment_id]
    assert updated_payment['status'] == PaymentService.STATUS_FAILED

    # Verify subscription status
    subscription = _db_subscriptions.get(user_id)
    assert subscription is not None
    assert subscription['status'] == PaymentService.SUBSCRIPTION_INACTIVE

def test_webhook_payment_refunded(client):
    """
    Tests processing a 'payment.refunded' webhook.
    Verifies that the payment status is updated to REFUNDED and
    any existing subscription for the user is set to INACTIVE.
    """
    user_id = "webhook_refund_user"
    amount = 25.00
    payment_id, gateway_id = _create_pending_payment(user_id, amount)
    event_id = str(uuid.uuid4())

    # First, make it succeeded and activate subscription to simulate a prior state
    _db_payments[payment_id]['status'] = PaymentService.STATUS_COMPLETED
    _db_subscriptions[user_id] = {
        "user_id": user_id,
        "status": PaymentService.SUBSCRIPTION_ACTIVE,
        "plan_id": "basic",
        "starts_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=10),
        "expires_at": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=20),
        "payment_id": payment_id,
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }

    payload = {
        "event_type": "payment.refunded",
        "gateway_id": gateway_id,
        "status": "refunded",
        "event_id": event_id
    }

    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['message'] == "Payment refunded and subscription deactivated."

    # Verify payment status
    updated_payment = _db_payments[payment_id]
    assert updated_payment['status'] == PaymentService.STATUS_REFUNDED

    # Verify subscription status
    subscription = _db_subscriptions.get(user_id)
    assert subscription is not None
    assert subscription['status'] == PaymentService.SUBSCRIPTION_INACTIVE


def test_webhook_unknown_gateway_id(client):
    """
    Tests webhook processing for a `gateway_id` that does not exist in our records.
    The endpoint should still return 200 OK (as is common for webhooks) but
    the message should indicate the issue and no database changes should occur.
    """
    payload = {
        "event_type": "payment.succeeded",
        "gateway_id": "unknown_gw_id",
        "status": "succeeded",
        "event_id": str(uuid.uuid4())
    }
    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 200 # Webhooks typically expect 200 even for internal errors
    data = json.loads(response.data)
    assert "Payment with gateway_id unknown_gw_id not found" in data['message']
    assert len(_db_payments) == 0 # No new payments should be created or updated if ID not found

def test_webhook_already_processed_succeeded(client):
    """
    Tests idempotency: sending a 'payment.succeeded' webhook twice for the same payment.
    The second call should be identified as already processed and should not alter the state
    of the payment or subscription, aside from potentially updating internal 'updated_at' timestamps.
    """
    user_id = "idempotent_user"
    amount = 75.00
    plan_id = "enterprise"
    payment_id, gateway_id = _create_pending_payment(user_id, amount, plan_id)
    event_id = str(uuid.uuid4())

    payload = {
        "event_type": "payment.succeeded",
        "gateway_id": gateway_id,
        "status": "succeeded",
        "event_id": event_id
    }

    # First webhook (should succeed and activate subscription)
    response1 = client.post('/api/payments/webhook', json=payload)
    assert response1.status_code == 200
    assert _db_payments[payment_id]['status'] == PaymentService.STATUS_COMPLETED
    assert _db_subscriptions[user_id]['status'] == PaymentService.SUBSCRIPTION_ACTIVE

    # Store initial updated_at for subscription to verify no change on second webhook (only payment gets updated_at on initial processing)
    initial_sub_updated_at = _db_subscriptions[user_id]['updated_at']

    # Second webhook with same event details (should be idempotent)
    response2 = client.post('/api/payments/webhook', json=payload)
    assert response2.status_code == 200
    data = json.loads(response2.data)
    assert data['message'] == "Payment already completed, no action needed (idempotent)."

    # Verify status remains COMPLETED and ACTIVE
    assert _db_payments[payment_id]['status'] == PaymentService.STATUS_COMPLETED
    assert _db_subscriptions[user_id]['status'] == PaymentService.SUBSCRIPTION_ACTIVE

    # Verify `updated_at` for subscription did not change (or changed minimally due to processing, but status is same)
    # The subscription should *not* be re-activated, so its updated_at should remain the same.
    assert _db_subscriptions[user_id]['updated_at'] == initial_sub_updated_at

def test_webhook_invalid_payload(client):
    """
    Tests webhook handling with invalid JSON payload or missing required fields.
    Ensures appropriate 400 Bad Request responses for malformed requests.
    """
    # Invalid JSON
    response = client.post('/api/payments/webhook', data="not json", content_type='application/json')
    assert response.status_code == 400
    assert "Invalid JSON payload" in json.loads(response.data)['error']

    # Missing event_type
    payload = {"gateway_id": "abc", "status": "succeeded"}
    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 400
    assert "Missing event_type, gateway_id, or status" in json.loads(response.data)['error']

    # Missing gateway_id
    payload = {"event_type": "payment.succeeded", "status": "succeeded"}
    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 400
    assert "Missing event_type, gateway_id, or status" in json.loads(response.data)['error']

    # Missing status
    payload = {"event_type": "payment.succeeded", "gateway_id": "abc"}
    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 400
    assert "Missing event_type, gateway_id, or status" in json.loads(response.data)['error']

def test_webhook_unknown_event_type(client):
    """
    Tests webhook processing with an unknown event type.
    The system should acknowledge receipt (200 OK) but indicate
    that the event type was not handled, and no state changes should occur.
    """
    user_id = "unknown_event_user"
    amount = 10.00
    payment_id, gateway_id = _create_pending_payment(user_id, amount)
    event_id = str(uuid.uuid4())

    payload = {
        "event_type": "subscription.deleted", # An event type not handled by our service
        "gateway_id": gateway_id,
        "status": "deleted",
        "event_id": event_id
    }
    response = client.post('/api/payments/webhook', json=payload)
    assert response.status_code == 200 # Still returns 200, but message indicates issue
    data = json.loads(response.data)
    assert "Unknown event type: subscription.deleted" in data['message']
    # Verify no status change for the payment
    assert _db_payments[payment_id]['status'] == PaymentService.STATUS_PENDING

# --- Test Get Payment and Subscription Details ---

def test_get_payment_details_existing(client):
    """
    Tests retrieving details for an existing payment via the API endpoint.
    """
    user_id = "detail_user"
    amount = 30.00
    payment_id, gateway_id = _create_pending_payment(user_id, amount)

    response = client.get(f'/api/payments/{payment_id}')
    assert response.status_code == 200
    data = json.loads(response.data)

    assert data['payment_id'] == payment_id
    assert data['user_id'] == user_id
    assert data['amount'] == amount
    assert data['status'] == PaymentService.STATUS_PENDING
    assert data['gateway_id'] == gateway_id

def test_get_payment_details_non_existent(client):
    """
    Tests retrieving details for a non-existent payment.
    Ensures a 404 Not Found response.
    """
    response = client.get('/api/payments/non_existent_payment_id')
    assert response.status_code == 404
    assert "Payment not found" in json.loads(response.data)['error']

def test_get_subscription_status_existing(client):
    """
    Tests retrieving status for an existing (active) subscription.
    """
    user_id = "sub_user_active"
    payment_id, gateway_id = _create_pending_payment(user_id, 100, "gold")
    # Manually activate subscription in the mock DB to set up the test state
    _db_payments[payment_id]['status'] = PaymentService.STATUS_COMPLETED
    _db_subscriptions[user_id] = {
        "user_id": user_id,
        "status": PaymentService.SUBSCRIPTION_ACTIVE,
        "plan_id": "gold",
        "starts_at": datetime.datetime.now(datetime.timezone.utc),
        "expires_at": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=30),
        "payment_id": payment_id,
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }

    response = client.get(f'/api/subscriptions/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user_id'] == user_id
    assert data['status'] == PaymentService.SUBSCRIPTION_ACTIVE
    assert data['plan_id'] == "gold"

def test_get_subscription_status_non_existent(client):
    """
    Tests retrieving status for a user with no subscription record.
    Should return an INACTIVE status with an informative message.
    """
    response = client.get('/api/subscriptions/non_existent_user')
    assert response.status_code == 200 # Returns 200 with inactive status as it's a valid query
    data = json.loads(response.data)
    assert data['status'] == PaymentService.SUBSCRIPTION_INACTIVE
    assert "No active subscription found" in data['message']

def test_get_subscription_status_inactive(client):
    """
    Tests retrieving status for a user with an explicitly inactive subscription.
    """
    user_id = "sub_user_inactive"
    payment_id, gateway_id = _create_pending_payment(user_id, 100)
    # Manually create an inactive subscription record
    _db_payments[payment_id]['status'] = PaymentService.STATUS_FAILED
    _db_subscriptions[user_id] = {
        "user_id": user_id,
        "status": PaymentService.SUBSCRIPTION_INACTIVE,
        "plan_id": "silver",
        "starts_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=60),
        "expires_at": datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=30),
        "payment_id": payment_id,
        "updated_at": datetime.datetime.now(datetime.timezone.utc),
    }

    response = client.get(f'/api/subscriptions/{user_id}')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['user_id'] == user_id
    assert data['status'] == PaymentService.SUBSCRIPTION_INACTIVE
    assert data['plan_id'] == "silver"