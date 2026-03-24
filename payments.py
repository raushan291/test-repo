import uuid
import datetime
import os
import sys

# Ensure `app` is importable by adding parent directory to path if necessary
# This might be needed if payments.py is in the same directory as app.py
# and tests need to import both, or if app.py imports payments.py.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

# --- Mock Database ---
# In-memory dictionary to simulate a database for payments and subscriptions
_db_payments = {}  # {payment_id: {user_id, amount, status, gateway_id, created_at, updated_at}}
_db_subscriptions = {} # {user_id: {status, plan_id, starts_at, expires_at, payment_id, updated_at}}

def _reset_db():
    """Resets the mock payment and subscription databases.
    Used for test isolation.
    """
    global _db_payments, _db_subscriptions
    _db_payments = {}
    _db_subscriptions = {}

# --- Mock Payment Gateway ---
class MockPaymentGateway:
    """
    A mock class to simulate interactions with an external payment gateway.
    It provides methods to create charges and (optionally) get payment status.
    """
    def create_charge(self, amount, user_id):
        """
        Simulates creating a charge with the payment gateway.
        Returns a dictionary with status, gateway_id, checkout_url, and error.
        A specific amount (1.01) can trigger a simulated failure.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number for gateway charge.")
        if amount == 1.01: # Special amount to simulate gateway failure
            return {"status": "failed", "gateway_id": None, "checkout_url": None, "error": "Gateway rejected transaction: insufficient funds"}
        
        gateway_id = "gw_" + str(uuid.uuid4())
        checkout_url = f"https://mock-gateway.com/checkout/{gateway_id}"
        return {"status": "pending", "gateway_id": gateway_id, "checkout_url": checkout_url, "error": None}

    def get_payment_status(self, gateway_id):
        """
        Simulates querying the gateway for payment status.
        For webhook testing, this might not be directly used by the service,
        as status updates are pushed via webhooks. Included for completeness.
        """
        if gateway_id == "mock_failed_gateway_id": # special id for testing specific scenarios
            return "failed"
        if gateway_id is None or not isinstance(gateway_id, str):
            raise ValueError("Invalid gateway ID provided.")
        return "succeeded" # Default mock behavior for successful payments

# Global instance of the mock gateway for direct use (can be overridden for testing)
mock_gateway = MockPaymentGateway()

# --- Payment Service ---
class PaymentService:
    """
    Handles payment initiation, webhook processing, and querying payment/subscription statuses.
    Interacts with the mock database and mock payment gateway.
    """
    # Payment Statuses
    STATUS_PENDING = "PENDING"
    STATUS_COMPLETED = "COMPLETED"
    STATUS_FAILED = "FAILED"
    STATUS_REFUNDED = "REFUNDED"
    STATUS_INITIATION_FAILED = "INITIATION_FAILED" # When gateway rejects or input is invalid

    # Subscription Statuses
    SUBSCRIPTION_ACTIVE = "ACTIVE"
    SUBSCRIPTION_INACTIVE = "INACTIVE"
    SUBSCRIPTION_CANCELLED = "CANCELLED"

    def __init__(self, gateway=None):
        """
        Initializes the PaymentService with a payment gateway.
        Allows dependency injection for testing.
        """
        self.gateway = gateway if gateway else mock_gateway

    def initiate_payment(self, user_id, amount, plan_id="basic"):
        """
        Initiates a payment by creating a record in the database
        and interacting with the payment gateway.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            # Record the attempt even if input is invalid
            payment_id = str(uuid.uuid4())
            created_at = datetime.datetime.now(datetime.timezone.utc)
            _db_payments[payment_id] = {
                "payment_id": payment_id,
                "user_id": user_id,
                "amount": amount,
                "plan_id": plan_id,
                "status": self.STATUS_INITIATION_FAILED,
                "gateway_id": None,
                "checkout_url": None,
                "error": "Amount must be a positive number.",
                "created_at": created_at,
                "updated_at": created_at,
            }
            return None, "Amount must be a positive number."
        
        if not isinstance(user_id, str) or not user_id:
            payment_id = str(uuid.uuid4())
            created_at = datetime.datetime.now(datetime.timezone.utc)
            _db_payments[payment_id] = {
                "payment_id": payment_id,
                "user_id": user_id,
                "amount": amount,
                "plan_id": plan_id,
                "status": self.STATUS_INITIATION_FAILED,
                "gateway_id": None,
                "checkout_url": None,
                "error": "User ID must be a non-empty string.",
                "created_at": created_at,
                "updated_at": created_at,
            }
            return None, "User ID must be a non-empty string."

        payment_id = str(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.timezone.utc)

        try:
            gateway_response = self.gateway.create_charge(amount, user_id)
            if gateway_response["status"] == "failed":
                _db_payments[payment_id] = {
                    "payment_id": payment_id,
                    "user_id": user_id,
                    "amount": amount,
                    "plan_id": plan_id,
                    "status": self.STATUS_INITIATION_FAILED,
                    "gateway_id": None,
                    "checkout_url": None,
                    "error": gateway_response.get("error"),
                    "created_at": created_at,
                    "updated_at": created_at,
                }
                return None, f"Payment initiation failed: {gateway_response.get('error', 'Unknown gateway error')}"

            _db_payments[payment_id] = {
                "payment_id": payment_id,
                "user_id": user_id,
                "amount": amount,
                "plan_id": plan_id,
                "status": self.STATUS_PENDING,
                "gateway_id": gateway_response["gateway_id"],
                "checkout_url": gateway_response["checkout_url"],
                "error": None,
                "created_at": created_at,
                "updated_at": created_at,
            }
            return gateway_response["checkout_url"], None
        except ValueError as e:
            # Catch errors from the mock gateway itself (e.g., if invalid amount passed to mock_gateway)
            _db_payments[payment_id] = {
                "payment_id": payment_id,
                "user_id": user_id,
                "amount": amount,
                "plan_id": plan_id,
                "status": self.STATUS_INITIATION_FAILED,
                "gateway_id": None,
                "checkout_url": None,
                "error": str(e),
                "created_at": created_at,
                "updated_at": created_at,
            }
            return None, str(e)


    def _update_payment_status(self, gateway_id, new_status, error=None):
        """
        Internal helper to update a payment record's status in the database.
        Identifies the payment by its gateway_id.
        """
        updated_at = datetime.datetime.now(datetime.timezone.utc)
        for payment_id, payment in _db_payments.items():
            if payment["gateway_id"] == gateway_id:
                payment["status"] = new_status
                payment["updated_at"] = updated_at
                if error:
                    payment["error"] = error
                return payment_id, payment["user_id"], payment["plan_id"]
        return None, None, None

    def _activate_subscription(self, user_id, plan_id, payment_id):
        """
        Activates or updates a user's subscription record.
        """
        updated_at = datetime.datetime.now(datetime.timezone.utc)
        starts_at = updated_at
        expires_at = starts_at + datetime.timedelta(days=30) # Simple 30-day subscription
        _db_subscriptions[user_id] = {
            "user_id": user_id,
            "status": self.SUBSCRIPTION_ACTIVE,
            "plan_id": plan_id,
            "starts_at": starts_at,
            "expires_at": expires_at,
            "payment_id": payment_id,
            "updated_at": updated_at,
        }

    def _deactivate_subscription(self, user_id):
        """
        Deactivates a user's subscription if it exists.
        """
        if user_id in _db_subscriptions:
            _db_subscriptions[user_id]["status"] = self.SUBSCRIPTION_INACTIVE
            _db_subscriptions[user_id]["updated_at"] = datetime.datetime.now(datetime.timezone.utc)

    def handle_webhook(self, event_type, gateway_id, payment_status, event_id=None):
        """
        Processes incoming payment gateway webhooks.
        Updates payment and subscription statuses based on the event type.
        Includes basic idempotency check for 'payment.succeeded'.
        """
        # In a real system, you'd verify the signature of the webhook payload
        # For this mock, we assume signature is verified externally or implicitly.

        # Find the payment by gateway_id and update its generic status first
        updated_payment_id, user_id, plan_id = self._update_payment_status(gateway_id, payment_status)

        if not updated_payment_id:
            return False, f"Payment with gateway_id {gateway_id} not found in our records."

        # Handle specific event types
        if event_type == "payment.succeeded":
            # Idempotency check: if payment is already completed, do nothing.
            if _db_payments[updated_payment_id]["status"] == self.STATUS_COMPLETED:
                return True, "Payment already completed, no action needed (idempotent)."
            
            _db_payments[updated_payment_id]["status"] = self.STATUS_COMPLETED
            self._activate_subscription(user_id, plan_id, updated_payment_id)
            return True, "Payment succeeded and subscription activated."
        elif event_type == "payment.failed":
            _db_payments[updated_payment_id]["status"] = self.STATUS_FAILED
            self._deactivate_subscription(user_id) # Ensure subscription is not active if payment fails
            return True, "Payment failed and subscription deactivated."
        elif event_type == "payment.refunded":
            _db_payments[updated_payment_id]["status"] = self.STATUS_REFUNDED
            self._deactivate_subscription(user_id)
            return True, "Payment refunded and subscription deactivated."
        else:
            return False, f"Unknown event type: {event_type}"

    def get_payment_details(self, payment_id):
        """
        Retrieves details for a specific payment by its internal ID.
        """
        return _db_payments.get(payment_id)

    def get_subscription_status(self, user_id):
        """
        Retrieves the subscription status for a specific user.
        """
        return _db_subscriptions.get(user_id)

# Global instance of the payment service for use within the Flask app
payment_service = PaymentService()