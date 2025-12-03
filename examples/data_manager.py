"""
Example Data Manager Module
Demonstrates wrapper functions and intermediate layers.
"""
from typing import List, Dict
from examples.database import DatabaseConnection
from examples.user_service import UserService


class DataManager:
    """Manages data operations across multiple services."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize data manager."""
        self.db = db_connection
        self.user_service = UserService(db_connection)
    
    def save_user_data(self, username: str, email: str) -> dict:
        """Save user data - calls UserService.create_user which calls insert."""
        # Level 2: save_user_data -> create_user -> insert
        return self.user_service.create_user(username, email)
    
    def save_audit_log(self, action: str, details: Dict) -> int:
        """Save audit log - directly calls insert."""
        # Level 1: Direct call to insert
        log_data = {
            'action': action,
            'details': str(details),
            'timestamp': 'now()'
        }
        return self.db.insert('audit_logs', log_data)
    
    def create_user_with_audit(self, username: str, email: str) -> dict:
        """Create user and log the action - calls both create_user and insert."""
        # Level 2 and 1: create_user_with_audit -> create_user -> insert
        #                create_user_with_audit -> insert (direct)
        user = self.user_service.create_user(username, email)
        self.save_audit_log('user_created', {'user_id': user.get('id')})
        return user


def create_user_wrapper(db: DatabaseConnection, username: str, email: str) -> dict:
    """Wrapper function that calls UserService.create_user."""
    # Level 3: create_user_wrapper -> UserService.create_user -> insert
    user_service = UserService(db)
    return user_service.create_user(username, email)


def bulk_user_operations(db: DatabaseConnection, users: List[dict]) -> List[int]:
    """Bulk operations that directly call insert multiple times."""
    # Level 1: Direct calls to insert
    user_ids = []
    for user in users:
        user_id = db.insert('users', user)
        user_ids.append(user_id)
    return user_ids

