"""
Example User Service Module
Demonstrates class structure and dependencies for impact analysis.
"""
from typing import List, Optional
from examples.database import DatabaseConnection
from examples.email_sender import EmailSender


class UserService:
    """Service class for user management operations."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize user service with database connection."""
        self.db = db_connection
        self.email_sender = EmailSender()
    
    def create_user(self, username: str, email: str) -> dict:
        """Create a new user."""
        user_data = {
            'username': username,
            'email': email,
            'status': 'active'
        }
        # Direct call to DatabaseConnection.insert
        user_id = self.db.insert('users', user_data)
        self.email_sender.send_welcome_email(email)
        return {'id': user_id, **user_data}
    
    def create_user_with_profile(self, username: str, email: str, profile_data: dict) -> dict:
        """Create user with profile - calls create_user which calls insert."""
        # Level 2: create_user_with_profile -> create_user -> insert
        user = self.create_user(username, email)
        # Also directly calls insert for profile
        profile_id = self.db.insert('user_profiles', {**profile_data, 'user_id': user['id']})
        user['profile_id'] = profile_id
        return user
    
    def get_user(self, user_id: int) -> Optional[dict]:
        """Retrieve a user by ID."""
        return self.db.query('users', {'id': user_id})
    
    def update_user(self, user_id: int, updates: dict) -> bool:
        """Update user information."""
        return self.db.update('users', user_id, updates)
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user."""
        return self.db.delete('users', user_id)
    
    def list_users(self) -> List[dict]:
        """List all users."""
        return self.db.query_all('users')


class UserValidator:
    """Utility class for validating user data."""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format."""
        return '@' in email and '.' in email.split('@')[1]
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format."""
        return len(username) >= 3 and username.isalnum()

