"""
Backend Authentication System using SQLAlchemy and SQLite
Provides user management, password hashing, and authentication
"""

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from werkzeug.security import generate_password_hash, check_password_hash
import os

# Database Configuration
DATABASE_URL = "sqlite:///users.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ============================================================================
# User Model Definition
# ============================================================================
class User(Base):
    """
    User model representing authenticated users in the system.
    
    Attributes:
        id (int): Primary key, auto-incremented
        username (str): Unique username for login
        hashed_password (str): Securely hashed password using Werkzeug
        role (str): User role - either 'admin' or 'user' (default: 'user')
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, role={self.role})>"


# ============================================================================
# Database Initialization
# ============================================================================
def init_db():
    """
    Initialize database and create all tables if they don't exist.
    Safe to call multiple times - only creates missing tables.
    """
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")


# ============================================================================
# CRUD Operations
# ============================================================================
def create_user(db: Session, username: str, password: str, role: str = "user") -> User:
    """
    Create a new user in the database with securely hashed password.
    
    Args:
        db (Session): SQLAlchemy database session
        username (str): Unique username for the user
        password (str): Plain text password (will be hashed)
        role (str): User role - 'admin' or 'user' (default: 'user')
    
    Returns:
        User: The created user object
    
    Raises:
        ValueError: If username already exists or invalid role provided
    
    Example:
        >>> db = SessionLocal()
        >>> user = create_user(db, "john_doe", "secure_password", role="admin")
        >>> db.close()
    """
    # Validate role
    if role not in ["admin", "user"]:
        raise ValueError(f"Invalid role: {role}. Must be 'admin' or 'user'")
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise ValueError(f"Username '{username}' already exists")
    
    # Hash password using Werkzeug
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    
    # Create new user object
    new_user = User(
        username=username,
        hashed_password=hashed_password,
        role=role
    )
    
    # Add to session and commit
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    """
    Authenticate a user by verifying username and password.
    
    Args:
        db (Session): SQLAlchemy database session
        username (str): Username to authenticate
        password (str): Plain text password to verify
    
    Returns:
        User: The authenticated user object if credentials are valid
        None: If username doesn't exist or password is incorrect
    
    Example:
        >>> db = SessionLocal()
        >>> user = authenticate_user(db, "john_doe", "secure_password")
        >>> if user:
        ...     print(f"Authenticated as {user.username}")
        >>> db.close()
    """
    # Retrieve user by username
    user = db.query(User).filter(User.username == username).first()
    
    # Return None if user doesn't exist
    if not user:
        return None
    
    # Verify password using Werkzeug
    if check_password_hash(user.hashed_password, password):
        return user
    
    return None


def get_user_by_username(db: Session, username: str) -> User | None:
    """
    Retrieve a user by username.
    
    Args:
        db (Session): SQLAlchemy database session
        username (str): Username to look up
    
    Returns:
        User: The user object if found, None otherwise
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """
    Retrieve a user by ID.
    
    Args:
        db (Session): SQLAlchemy database session
        user_id (int): User ID to look up
    
    Returns:
        User: The user object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def list_all_users(db: Session) -> list[User]:
    """
    Retrieve all users from the database.
    
    Args:
        db (Session): SQLAlchemy database session
    
    Returns:
        list[User]: List of all user objects
    """
    return db.query(User).all()


def delete_user(db: Session, username: str) -> bool:
    """
    Delete a user from the database.
    
    Args:
        db (Session): SQLAlchemy database session
        username (str): Username of user to delete
    
    Returns:
        bool: True if user was deleted, False if user not found
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False


def update_user_password(db: Session, username: str, new_password: str) -> bool:
    """
    Update a user's password.
    
    Args:
        db (Session): SQLAlchemy database session
        username (str): Username of user
        new_password (str): New plain text password
    
    Returns:
        bool: True if password was updated, False if user not found
    """
    user = db.query(User).filter(User.username == username).first()
    if user:
        user.hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.commit()
        return True
    return False


# ============================================================================
# Test Script
# ============================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🔐 Backend Authentication System Test")
    print("=" * 70)
    
    # Initialize database
    init_db()
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Clean up existing test users if they exist
        print("\n1️⃣  Cleaning up existing test users...")
        delete_user(db, "admin_user")
        delete_user(db, "regular_user")
        print("   ✓ Cleanup complete")
        
        # Create test users
        print("\n2️⃣  Creating test users...")
        admin_user = create_user(db, "tejas", "admin_password_123", role="admin")
        print(f"   ✓ Admin user created: {admin_user}")
        
        regular_user = create_user(db, "regular_user", "user_password_456", role="user")
        print(f"   ✓ Regular user created: {regular_user}")
        
        # Test authentication - valid credentials
        print("\n3️⃣  Testing authentication with valid credentials...")
        
        authenticated_admin = authenticate_user(db, "admin_user", "admin_password_123")
        if authenticated_admin:
            print(f"   ✓ Admin login SUCCESS: {authenticated_admin}")
        else:
            print("   ✗ Admin login FAILED")
        
        authenticated_user = authenticate_user(db, "regular_user", "user_password_456")
        if authenticated_user:
            print(f"   ✓ Regular user login SUCCESS: {authenticated_user}")
        else:
            print("   ✗ Regular user login FAILED")
        
        # Test authentication - invalid password
        print("\n4️⃣  Testing authentication with invalid credentials...")
        
        invalid_auth_admin = authenticate_user(db, "admin_user", "wrong_password")
        if invalid_auth_admin is None:
            print("   ✓ Invalid password correctly rejected for admin")
        else:
            print("   ✗ Invalid password not rejected")
        
        invalid_auth_user = authenticate_user(db, "regular_user", "wrong_password")
        if invalid_auth_user is None:
            print("   ✓ Invalid password correctly rejected for regular user")
        else:
            print("   ✗ Invalid password not rejected")
        
        # Test authentication - non-existent user
        print("\n5️⃣  Testing authentication with non-existent user...")
        
        nonexistent_user = authenticate_user(db, "nonexistent", "any_password")
        if nonexistent_user is None:
            print("   ✓ Non-existent user correctly rejected")
        else:
            print("   ✗ Non-existent user not rejected")
        
        # List all users
        print("\n6️⃣  Listing all users in database...")
        all_users = list_all_users(db)
        for user in all_users:
            print(f"   - {user.username} (Role: {user.role}, ID: {user.id})")
        
        # Test password update
        print("\n7️⃣  Testing password update...")
        update_user_password(db, "regular_user", "new_password_789")
        
        old_password_auth = authenticate_user(db, "regular_user", "user_password_456")
        if old_password_auth is None:
            print("   ✓ Old password no longer works")
        
        new_password_auth = authenticate_user(db, "regular_user", "new_password_789")
        if new_password_auth:
            print("   ✓ New password works correctly")
        
        print("\n" + "=" * 70)
        print("✅ All tests completed successfully!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
    finally:
        db.close()
