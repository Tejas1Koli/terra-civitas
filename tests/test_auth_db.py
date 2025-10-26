"""
Unit tests for auth/db.py - Authentication system
"""

import pytest
from auth.db import (
    init_db, create_user, authenticate_user, get_user_by_username,
    get_user_by_id, list_all_users, delete_user, update_user_password,
    User, SessionLocal, Base, engine
)
import os
import tempfile
import sqlite3


class TestUserModel:
    """Test User ORM model"""
    
    def test_user_model_creation(self):
        """Test User model can be instantiated"""
        user = User(username="test_user", hashed_password="hashed", role="user")
        assert user.username == "test_user"
        assert user.role == "user"
    
    def test_user_repr(self):
        """Test User string representation"""
        user = User(id=1, username="test_user", hashed_password="hashed", role="admin")
        repr_str = repr(user)
        assert "test_user" in repr_str
        assert "admin" in repr_str


class TestDatabaseInit:
    """Test database initialization"""
    
    def test_init_db_creates_tables(self, tmp_path):
        """Test that init_db creates necessary tables"""
        db_file = tmp_path / "test.db"
        os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"
        
        init_db()
        
        # Verify tables were created
        assert db_file.exists()
        conn = sqlite3.connect(str(db_file))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None


class TestCreateUser:
    """Test user creation functionality"""
    
    def test_create_user_success(self):
        """Test successful user creation"""
        db = SessionLocal()
        try:
            user = create_user(db, "newuser", "password123", role="user")
            assert user.username == "newuser"
            assert user.role == "user"
            assert user.hashed_password != "password123"  # Password should be hashed
        finally:
            delete_user(db, "newuser")
            db.close()
    
    def test_create_admin_user(self):
        """Test admin user creation"""
        db = SessionLocal()
        try:
            user = create_user(db, "adminuser", "adminpass", role="admin")
            assert user.role == "admin"
        finally:
            delete_user(db, "adminuser")
            db.close()
    
    def test_create_user_duplicate_username(self):
        """Test that duplicate usernames raise error"""
        db = SessionLocal()
        try:
            create_user(db, "dupuser", "password1", role="user")
            with pytest.raises(ValueError, match="already exists"):
                create_user(db, "dupuser", "password2", role="user")
        finally:
            delete_user(db, "dupuser")
            db.close()
    
    def test_create_user_invalid_role(self):
        """Test that invalid roles raise error"""
        db = SessionLocal()
        with pytest.raises(ValueError, match="Invalid role"):
            create_user(db, "testuser", "password", role="superuser")
        db.close()
    
    def test_create_user_default_role(self):
        """Test that default role is 'user'"""
        db = SessionLocal()
        try:
            user = create_user(db, "defaultrole", "password")
            assert user.role == "user"
        finally:
            delete_user(db, "defaultrole")
            db.close()


class TestAuthenticateUser:
    """Test user authentication"""
    
    def test_authenticate_user_valid_credentials(self):
        """Test authentication with valid credentials"""
        db = SessionLocal()
        try:
            create_user(db, "authuser", "correctpass", role="user")
            user = authenticate_user(db, "authuser", "correctpass")
            assert user is not None
            assert user.username == "authuser"
        finally:
            delete_user(db, "authuser")
            db.close()
    
    def test_authenticate_user_invalid_password(self):
        """Test authentication with wrong password"""
        db = SessionLocal()
        try:
            create_user(db, "authuser", "correctpass", role="user")
            user = authenticate_user(db, "authuser", "wrongpass")
            assert user is None
        finally:
            delete_user(db, "authuser")
            db.close()
    
    def test_authenticate_user_nonexistent(self):
        """Test authentication with non-existent user"""
        db = SessionLocal()
        user = authenticate_user(db, "nonexistent", "anypass")
        assert user is None
        db.close()
    
    def test_authenticate_admin_user(self):
        """Test authentication for admin user"""
        db = SessionLocal()
        try:
            create_user(db, "admin", "adminpass", role="admin")
            user = authenticate_user(db, "admin", "adminpass")
            assert user is not None
            assert user.role == "admin"
        finally:
            delete_user(db, "admin")
            db.close()


class TestGetUser:
    """Test user retrieval methods"""
    
    def test_get_user_by_username(self):
        """Test retrieving user by username"""
        db = SessionLocal()
        try:
            created_user = create_user(db, "gettest", "password", role="user")
            retrieved_user = get_user_by_username(db, "gettest")
            assert retrieved_user is not None
            assert retrieved_user.username == "gettest"
        finally:
            delete_user(db, "gettest")
            db.close()
    
    def test_get_user_by_username_nonexistent(self):
        """Test retrieving non-existent user by username"""
        db = SessionLocal()
        user = get_user_by_username(db, "nonexistent")
        assert user is None
        db.close()
    
    def test_get_user_by_id(self):
        """Test retrieving user by ID"""
        db = SessionLocal()
        try:
            created_user = create_user(db, "getbyid", "password", role="user")
            retrieved_user = get_user_by_id(db, created_user.id)
            assert retrieved_user is not None
            assert retrieved_user.id == created_user.id
        finally:
            delete_user(db, "getbyid")
            db.close()
    
    def test_get_user_by_id_nonexistent(self):
        """Test retrieving non-existent user by ID"""
        db = SessionLocal()
        user = get_user_by_id(db, 9999)
        assert user is None
        db.close()


class TestListUsers:
    """Test listing users"""
    
    def test_list_all_users(self):
        """Test retrieving all users"""
        db = SessionLocal()
        try:
            initial_count = len(list_all_users(db))
            create_user(db, "user1", "pass1")
            create_user(db, "user2", "pass2")
            
            all_users = list_all_users(db)
            assert len(all_users) >= initial_count + 2
        finally:
            delete_user(db, "user1")
            delete_user(db, "user2")
            db.close()
    
    def test_list_users_empty_or_nonempty(self):
        """Test list_all_users returns a list"""
        db = SessionLocal()
        users = list_all_users(db)
        assert isinstance(users, list)
        db.close()


class TestDeleteUser:
    """Test user deletion"""
    
    def test_delete_user_success(self):
        """Test successful user deletion"""
        db = SessionLocal()
        create_user(db, "todelete", "password", role="user")
        result = delete_user(db, "todelete")
        assert result is True
        
        # Verify user is deleted
        user = get_user_by_username(db, "todelete")
        assert user is None
        db.close()
    
    def test_delete_user_nonexistent(self):
        """Test deleting non-existent user"""
        db = SessionLocal()
        result = delete_user(db, "nonexistent")
        assert result is False
        db.close()


class TestUpdatePassword:
    """Test password update functionality"""
    
    def test_update_user_password_success(self):
        """Test successful password update"""
        db = SessionLocal()
        try:
            create_user(db, "passtest", "oldpass", role="user")
            
            # Verify old password works
            user = authenticate_user(db, "passtest", "oldpass")
            assert user is not None
            
            # Update password
            result = update_user_password(db, "passtest", "newpass")
            assert result is True
            
            # Verify old password doesn't work
            user = authenticate_user(db, "passtest", "oldpass")
            assert user is None
            
            # Verify new password works
            user = authenticate_user(db, "passtest", "newpass")
            assert user is not None
        finally:
            delete_user(db, "passtest")
            db.close()
    
    def test_update_password_nonexistent_user(self):
        """Test updating password for non-existent user"""
        db = SessionLocal()
        result = update_user_password(db, "nonexistent", "newpass")
        assert result is False
        db.close()


class TestPasswordHashing:
    """Test password hashing security"""
    
    def test_passwords_are_hashed(self):
        """Test that passwords are hashed, not stored plaintext"""
        db = SessionLocal()
        try:
            password = "cleartextpassword"
            user = create_user(db, "hashtest", password, role="user")
            
            # Password should not be stored plaintext
            assert user.hashed_password != password
            # Hashed password should be different each time (salt)
            user2 = create_user(db, "hashtest2", password, role="user")
            assert user.hashed_password != user2.hashed_password
        finally:
            delete_user(db, "hashtest")
            delete_user(db, "hashtest2")
            db.close()
    
    def test_hash_consistency(self):
        """Test that same password correctly verifies"""
        db = SessionLocal()
        try:
            password = "testpassword123"
            create_user(db, "hashcon", password, role="user")
            
            # Same password should authenticate
            user1 = authenticate_user(db, "hashcon", password)
            assert user1 is not None
            
            # Slightly different password should not authenticate
            user2 = authenticate_user(db, "hashcon", password + "x")
            assert user2 is None
        finally:
            delete_user(db, "hashcon")
            db.close()
