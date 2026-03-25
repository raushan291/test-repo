import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError, OperationalError

# Adjust import based on the actual file structure.
# Assuming `models.py` is in the parent directory of `tests/`.
# If `models.py` is at the project root, and tests are run from root,
# `from models import Base, User, Subscription, Payment` might work.
# For robust imports in a typical project structure, use relative import.
from models import Base, User, Subscription, Payment 

@pytest.fixture(scope='session')
def engine():
    """
    Fixture to create an in-memory SQLite engine for testing.
    Uses StaticPool to ensure the same connection is used across all threads for in-memory DBs,
    preventing issues where multiple connections create separate databases.
    """
    return create_engine("sqlite:///:memory:", poolclass=StaticPool)

@pytest.fixture(scope='session')
def tables(engine):
    """
    Fixture to create all tables before tests in the session and drop them afterwards.
    Ensures a clean schema for the entire test run.
    """
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def session(engine, tables):
    """
    Fixture to provide a SQLAlchemy session for each test.
    Each test gets its own session, and transactions are rolled back after each test
    to ensure test isolation and a clean database state.
    """
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()

    yield session

    session.close()
    transaction.rollback() # Rollback changes to keep the database state clean for the next test
    connection.close()

def test_user_creation(session):
    """Test that a user can be created and retrieved correctly with all fields."""
    user = User(
        email='test@example.com',
        password_hash='hashed_password_123',
        roles='admin,user'
    )
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(email='test@example.com').first()
    assert retrieved_user is not None
    assert retrieved_user.email == 'test@example.com'
    assert retrieved_user.password_hash == 'hashed_password_123'
    assert retrieved_user.is_active is True
    assert retrieved_user.roles == 'admin,user'
    assert isinstance(retrieved_user.created_at, datetime)
    assert retrieved_user.id is not None

def test_user_default_values(session):
    """Test that default values for User fields are applied correctly."""
    user = User(email='default_user@example.com', password_hash='default_hash')
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(email='default_user@example.com').first()
    assert retrieved_user.is_active is True
    assert retrieved_user.roles == 'user'
    assert isinstance(retrieved_user.created_at, datetime)

def test_user_email_uniqueness_failure(session):
    """
    Test that attempting to create two users with the same email address
    raises an IntegrityError due to the unique constraint.
    """
    user1 = User(email='unique@example.com', password_hash='hash1')
    session.add(user1)
    session.commit()

    user2 = User(email='unique@example.com', password_hash='hash2')
    session.add(user2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback() # Rollback the failed transaction

def test_subscription_creation(session):
    """Test creating a subscription linked to an existing user."""
    user = User(email='sub_user@example.com', password_hash='sub_hash')
    session.add(user)
    session.commit() # Commit user to get an ID

    # Define an end date for testing
    future_date = datetime.now() + timedelta(days=30)
    subscription = Subscription(
        user_id=user.id,
        tier='premium',
        end_date=future_date
    )
    session.add(subscription)
    session.commit()

    retrieved_subscription = session.query(Subscription).filter_by(user_id=user.id).first()
    assert retrieved_subscription is not None
    assert retrieved_subscription.user_id == user.id
    assert retrieved_subscription.tier == 'premium'
    assert retrieved_subscription.is_active is True
    assert isinstance(retrieved_subscription.start_date, datetime)
    assert retrieved_subscription.end_date.date() == future_date.date() # Compare dates only
    assert retrieved_subscription.id is not None

def test_subscription_defaults(session):
    """Test default values for Subscription fields."""
    user = User(email='default_sub_user@example.com', password_hash='default_sub_hash')
    session.add(user)
    session.commit()

    subscription = Subscription(user_id=user.id, tier='free')
    session.add(subscription)
    session.commit()

    retrieved_subscription = session.query(Subscription).filter_by(id=subscription.id).first()
    assert retrieved_subscription.is_active is True
    assert isinstance(retrieved_subscription.start_date, datetime)
    assert retrieved_subscription.end_date is None # Should be None as not provided

def test_payment_creation(session):
    """Test creating a payment linked to an existing user with decimal amount."""
    user = User(email='pay_user@example.com', password_hash='pay_hash')
    session.add(user)
    session.commit() # Commit user to get an ID

    payment = Payment(
        user_id=user.id,
        amount=Decimal('50.00'), # Use Decimal for amount
        currency='EUR',
        transaction_id='txn_12345'
    )
    session.add(payment)
    session.commit()

    retrieved_payment = session.query(Payment).filter_by(user_id=user.id).first()
    assert retrieved_payment is not None
    assert retrieved_payment.user_id == user.id
    assert retrieved_payment.amount == Decimal('50.00')
    assert retrieved_payment.currency == 'EUR'
    assert retrieved_payment.status == 'completed'
    assert retrieved_payment.transaction_id == 'txn_12345'
    assert isinstance(retrieved_payment.payment_date, datetime)
    assert retrieved_payment.id is not None

def test_payment_defaults(session):
    """Test default values for Payment fields."""
    user = User(email='default_pay_user@example.com', password_hash='default_pay_hash')
    session.add(user)
    session.commit()

    payment = Payment(user_id=user.id, amount=Decimal('1.00'), transaction_id='default_txn')
    session.add(payment)
    session.commit()

    retrieved_payment = session.query(Payment).filter_by(id=payment.id).first()
    assert retrieved_payment.currency == 'USD'
    assert retrieved_payment.status == 'completed'
    assert isinstance(retrieved_payment.payment_date, datetime)

def test_payment_transaction_id_uniqueness_failure(session):
    """
    Test that creating two payments with the same transaction_id
    raises an IntegrityError.
    """
    user = User(email='txn_fail_user@example.com', password_hash='txn_fail_hash')
    session.add(user)
    session.commit()

    payment1 = Payment(user_id=user.id, amount=Decimal('10.00'), transaction_id='unique_txn_id')
    session.add(payment1)
    session.commit()

    payment2 = Payment(user_id=user.id, amount=Decimal('20.00'), transaction_id='unique_txn_id')
    session.add(payment2)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_user_relationships_one_to_many(session):
    """
    Test the one-to-many relationships from User to Subscription and Payment,
    verifying that associated entities are correctly linked.
    """
    user = User(email='rel_user@example.com', password_hash='rel_hash')
    session.add(user)
    session.commit() # Commit user to get an ID

    sub1 = Subscription(user_id=user.id, tier='basic')
    sub2 = Subscription(user_id=user.id, tier='pro')
    pay1 = Payment(user_id=user.id, amount=Decimal('10.00'), transaction_id='txn_a')
    pay2 = Payment(user_id=user.id, amount=Decimal('20.00'), transaction_id='txn_b')

    session.add_all([sub1, sub2, pay1, pay2])
    session.commit()

    # Refresh the user object to load the relationships
    retrieved_user = session.query(User).filter_by(id=user.id).first()
    assert retrieved_user is not None
    assert len(retrieved_user.subscriptions) == 2
    assert {s.tier for s in retrieved_user.subscriptions} == {'basic', 'pro'}

    assert len(retrieved_user.payments) == 2
    assert {p.amount for p in retrieved_user.payments} == {Decimal('10.00'), Decimal('20.00')}

def test_subscription_user_relationship_many_to_one(session):
    """Test the many-to-one relationship from Subscription to User."""
    user = User(email='sub_rel_user@example.com', password_hash='sub_rel_hash')
    session.add(user)
    session.commit()

    subscription = Subscription(user_id=user.id, tier='basic')
    session.add(subscription)
    session.commit()

    retrieved_subscription = session.query(Subscription).filter_by(id=subscription.id).first()
    assert retrieved_subscription.user is not None
    assert retrieved_subscription.user.email == user.email

def test_payment_user_relationship_many_to_one(session):
    """Test the many-to-one relationship from Payment to User."""
    user = User(email='pay_rel_user@example.com', password_hash='pay_rel_hash')
    session.add(user)
    session.commit()

    payment = Payment(user_id=user.id, amount=Decimal('75.00'), transaction_id='txn_xyz')
    session.add(payment)
    session.commit()

    retrieved_payment = session.query(Payment).filter_by(id=payment.id).first()
    assert retrieved_payment.user is not None
    assert retrieved_payment.user.email == user.email

def test_no_related_entities(session):
    """
    Test that a user created without any payments or subscriptions
    has empty relationship lists.
    """
    user = User(email='empty_rel_user@example.com', password_hash='empty_rel_hash')
    session.add(user)
    session.commit()

    retrieved_user = session.query(User).filter_by(id=user.id).first()
    assert retrieved_user is not None
    assert len(retrieved_user.subscriptions) == 0
    assert len(retrieved_user.payments) == 0

def test_user_deletion_cascade(session):
    """
    Test that deleting a user also cascades to delete their associated
    subscriptions and payments due to `cascade="all, delete-orphan"`.
    """
    user = User(email='cascade_user@example.com', password_hash='cascade_hash')
    session.add(user)
    session.commit() # Need ID for foreign keys

    sub = Subscription(user_id=user.id, tier='gold')
    pay = Payment(user_id=user.id, amount=Decimal('100.00'), transaction_id='txn_cascade')
    session.add_all([sub, pay])
    session.commit()

    # Verify entities exist before deletion
    assert session.query(User).count() == 1
    assert session.query(Subscription).count() == 1
    assert session.query(Payment).count() == 1

    session.delete(user)
    session.commit()

    # Verify entities are deleted after user deletion
    assert session.query(User).count() == 0
    assert session.query(Subscription).count() == 0
    assert session.query(Payment).count() == 0

def test_nullable_fields_for_subscription(session):
    """Test that nullable fields (like end_date) can be left None."""
    user = User(email='nullable_sub_user@example.com', password_hash='hash')
    session.add(user)
    session.commit()

    subscription = Subscription(user_id=user.id, tier='basic', end_date=None)
    session.add(subscription)
    session.commit()

    retrieved_sub = session.query(Subscription).filter_by(id=subscription.id).first()
    assert retrieved_sub.end_date is None

def test_non_nullable_fields_violation_for_user(session):
    """Test that creating a user without a required field (email) raises an IntegrityError."""
    user = User(email=None, password_hash='hash') # Email is nullable=False
    session.add(user)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_non_nullable_fields_violation_for_payment(session):
    """Test that creating a payment without a required field (amount) raises an IntegrityError."""
    user = User(email='non_nullable@example.com', password_hash='hash')
    session.add(user)
    session.commit()

    payment = Payment(user_id=user.id, amount=None, transaction_id='txn_no_amount') # Amount is nullable=False
    session.add(payment)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()

def test_non_existent_foreign_key(session):
    """Test adding a subscription with a user_id that does not exist."""
    subscription = Subscription(user_id=999, tier='basic') # User ID 999 does not exist
    session.add(subscription)
    with pytest.raises(IntegrityError):
        session.commit()
    session.rollback()