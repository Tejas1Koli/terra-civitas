# Backend Authentication System - Usage Guide

## Overview
Complete authentication system using SQLAlchemy ORM and SQLite with Werkzeug password hashing.

## Files Created
- `auth/db.py` - Main authentication module with User model, database setup, and CRUD operations
- `auth/__init__.py` - Module exports for easy importing

## Database Setup
```python
from auth import init_db, SessionLocal

# Initialize database (creates tables if not exist)
init_db()

# Get a database session
db = SessionLocal()
# ... perform operations ...
db.close()
```

## Creating Users
```python
from auth import create_user, SessionLocal

db = SessionLocal()

# Create a regular user
user = create_user(db, "john_doe", "secure_password", role="user")

# Create an admin user
admin = create_user(db, "admin_user", "admin_password", role="admin")

db.close()
```

## Authenticating Users
```python
from auth import authenticate_user, SessionLocal

db = SessionLocal()

# Attempt authentication
user = authenticate_user(db, "john_doe", "secure_password")

if user:
    print(f"Logged in as {user.username} ({user.role})")
else:
    print("Authentication failed")

db.close()
```

## Other Operations
```python
from auth import (
    get_user_by_username,
    get_user_by_id,
    list_all_users,
    update_user_password,
    delete_user,
    SessionLocal
)

db = SessionLocal()

# Get user by username
user = get_user_by_username(db, "john_doe")

# Get user by ID
user = get_user_by_id(db, 1)

# List all users
all_users = list_all_users(db)

# Update password
update_user_password(db, "john_doe", "new_password")

# Delete user
delete_user(db, "john_doe")

db.close()
```

## User Model
```python
class User:
    id: int              # Primary key
    username: str        # Unique username
    hashed_password: str # Securely hashed with Werkzeug
    role: str           # 'admin' or 'user'
```

## Database File
- Location: `users.db` (SQLite)
- Automatically created on first run
- Stores all user credentials

## Security Features
- ✅ Password hashing using Werkzeug (pbkdf2:sha256)
- ✅ Salted hashes with configurable iterations
- ✅ SQL injection prevention via SQLAlchemy ORM
- ✅ Unique username constraint at database level
- ✅ Role-based access control support

## Testing
Run the included test script:
```bash
python auth/db.py
```

This will:
1. Create admin and regular users
2. Test valid/invalid authentication
3. Test non-existent users
4. List all users
5. Test password updates

## Integration with FastAPI/Streamlit
```python
from auth import authenticate_user, SessionLocal

# In your FastAPI endpoint or Streamlit app
db = SessionLocal()
user = authenticate_user(db, username, password)

if user:
    # User authenticated successfully
    session_data = {"user_id": user.id, "role": user.role}
else:
    # Authentication failed
    raise Exception("Invalid credentials")

db.close()
```

## Dependencies
- SQLAlchemy >= 2.0
- Werkzeug >= 3.0
- Python 3.8+
