"""
Example Order Service Module
Demonstrates multi-level dependencies and cross-file usage.
"""
from typing import List, Optional
from examples.database import DatabaseConnection


class OrderService:
    """Service class for order management operations."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize order service with database connection."""
        self.db = db_connection
    
    def create_order(self, user_id: int, items: List[dict]) -> dict:
        """Create a new order."""
        order_data = {
            'user_id': user_id,
            'items': str(items),
            'status': 'pending'
        }
        # Direct call to DatabaseConnection.insert
        order_id = self.db.insert('orders', order_data)
        return {'id': order_id, **order_data}
    
    def create_order_with_validation(self, user_id: int, items: List[dict]) -> Optional[dict]:
        """Create order with validation - calls create_order which calls insert."""
        if user_id > 0 and len(items) > 0:
            return self.create_order(user_id, items)
        return None
    
    def bulk_create_orders(self, orders: List[dict]) -> List[int]:
        """Create multiple orders - each calls insert."""
        order_ids = []
        for order in orders:
            order_id = self.db.insert('orders', order)
            order_ids.append(order_id)
        return order_ids


class OrderProcessor:
    """Processes orders with multiple steps."""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize order processor."""
        self.db = db_connection
        self.order_service = OrderService(db_connection)
    
    def process_new_order(self, user_id: int, items: List[dict]) -> dict:
        """Process a new order - calls OrderService which calls insert."""
        # Level 2: process_new_order -> create_order -> insert
        return self.order_service.create_order(user_id, items)
    
    def process_order_with_validation(self, user_id: int, items: List[dict]) -> Optional[dict]:
        """Process order with validation - calls create_order_with_validation -> create_order -> insert."""
        # Level 3: process_order_with_validation -> create_order_with_validation -> create_order -> insert
        return self.order_service.create_order_with_validation(user_id, items)
    
    def process_bulk_orders(self, orders: List[dict]) -> List[int]:
        """Process multiple orders - calls bulk_create_orders -> insert."""
        # Level 2: process_bulk_orders -> bulk_create_orders -> insert (multiple times)
        return self.order_service.bulk_create_orders(orders)




