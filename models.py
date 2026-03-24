import uuid
from datetime import datetime, timedelta

# In-memory "database" for demonstration purposes
# In a real application, these would be SQLAlchemy models or similar, backed by a persistent database.
_users_db = {}
_subscriptions_db = {}
_payments_db = {}

class User:
    """
    Mock User model for demonstration.
    """
    def __init__(self, id=None, email=None):
        self.id = id if id else str(uuid.uuid4())
        self.email = email
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        _users_db[self.id] = self

    def save(self):
        """Saves or updates the user in the mock database."""
        self.updated_at = datetime.utcnow()
        _users_db[self.id] = self
        return self

    @staticmethod
    def get(user_id):
        """Retrieves a user by their ID."""
        return _users_db.get(user_id)

    @staticmethod
    def get_by_email(email):
        """Retrieves a user by their email."""
        for user in _users_db.values():
            if user.email == email:
                return user
        return None

    @staticmethod
    def create(email):
        """Creates a new user."""
        user = User(email=email)
        user.save()
        return user

    @staticmethod
    def reset_for_tests():
        """Clears all user data for testing."""
        _users_db.clear()


class Subscription:
    """
    Mock Subscription model for demonstration.
    """
    def __init__(self, id=None, user_id=None, plan_id=None,
                 gateway_subscription_id=None, status='pending',
                 start_date=None, end_date=None):
        self.id = id if id else str(uuid.uuid4())
        self.user_id = user_id
        self.plan_id = plan_id # e.g., 'premium_monthly', 'basic_annual'
        self.gateway_subscription_id = gateway_subscription_id # e.g., Stripe subscription ID
        self.status = status # e.g., 'pending', 'active', 'cancelled', 'expired', 'past_due'
        self.start_date = start_date if start_date else datetime.utcnow()
        self.end_date = end_date # For fixed term or calculated for recurring (e.g., next billing date)
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        _subscriptions_db[self.id] = self

    def save(self):
        """Saves or updates the subscription in the mock database."""
        self.updated_at = datetime.utcnow()
        _subscriptions_db[self.id] = self
        return self

    @staticmethod
    def get(subscription_id):
        """Retrieves a subscription by its ID."""
        return _subscriptions_db.get(subscription_id)

    @staticmethod
    def get_by_gateway_id(gateway_subscription_id):
        """Retrieves a subscription by its payment gateway's subscription ID."""
        for sub in _subscriptions_db.values():
            if sub.gateway_subscription_id == gateway_subscription_id:
                return sub
        return None

    @staticmethod
    def create(user_id, plan_id, gateway_subscription_id, status='active'):
        """Creates a new subscription."""
        # For a monthly plan, set end date 1 month from now as an example
        end_date = datetime.utcnow() + timedelta(days=30)
        subscription = Subscription(
            user_id=user_id,
            plan_id=plan_id,
            gateway_subscription_id=gateway_subscription_id,
            status=status,
            start_date=datetime.utcnow(),
            end_date=end_date
        )
        subscription.save()
        return subscription

    @staticmethod
    def reset_for_tests():
        """Clears all subscription data for testing."""
        _subscriptions_db.clear()


class Payment:
    """
    Mock Payment model for demonstration.
    """
    def __init__(self, id=None, user_id=None, amount=None, currency=None,
                 gateway_transaction_id=None, status='pending',
                 payment_type='one_time', subscription_id=None):
        self.id = id if id else str(uuid.uuid4())
        self.user_id = user_id
        self.amount = amount # stored as cents/smallest unit (e.g., 1000 for $10.00)
        self.currency = currency # e.g., 'usd'
        self.gateway_transaction_id = gateway_transaction_id # e.g., Stripe Payment Intent ID or Charge ID
        self.status = status # e.g., 'pending', 'succeeded', 'failed', 'refunded'
        self.payment_type = payment_type # 'one_time', 'subscription_initial', 'subscription_recurring'
        self.subscription_id = subscription_id # Link to Subscription if applicable
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        _payments_db[self.id] = self

    def save(self):
        """Saves or updates the payment in the mock database."""
        self.updated_at = datetime.utcnow()
        _payments_db[self.id] = self
        return self

    @staticmethod
    def get(payment_id):
        """Retrieves a payment by its ID."""
        return _payments_db.get(payment_id)

    @staticmethod
    def get_by_gateway_id(gateway_transaction_id):
        """Retrieves a payment by its payment gateway's transaction ID."""
        for payment in _payments_db.values():
            if payment.gateway_transaction_id == gateway_transaction_id:
                return payment
        return None

    @staticmethod
    def create(user_id, amount, currency, gateway_transaction_id,
               status='succeeded', payment_type='one_time', subscription_id=None):
        """Creates a new payment record."""
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            gateway_transaction_id=gateway_transaction_id,
            status=status,
            payment_type=payment_type,
            subscription_id=subscription_id
        )
        payment.save()
        return payment

    @staticmethod
    def reset_for_tests():
        """Clears all payment data for testing."""
        _payments_db.clear()


def reset_all_models_for_tests():
    """Resets all mock database models for a clean test state."""
    User.reset_for_tests()
    Subscription.reset_for_tests()
    Payment.reset_for_tests()