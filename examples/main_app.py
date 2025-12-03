"""
Example Main Application
Demonstrates how different modules interact with each other.
"""
from examples.user_service import UserService, UserValidator
from examples.database import DatabaseConnection
from examples.order_service import OrderService, OrderProcessor
from examples.data_manager import DataManager, create_user_wrapper, bulk_user_operations


def setup_application():
    """Initialize application components."""
    db = DatabaseConnection('example.db')
    user_service = UserService(db)
    order_service = OrderService(db)
    order_processor = OrderProcessor(db)
    data_manager = DataManager(db)
    return user_service, order_service, order_processor, data_manager, db


def create_sample_user():
    """Create a sample user - calls setup_application then create_user."""
    # Level 3: create_sample_user -> setup_application -> UserService.create_user -> insert
    user_service, _, _, _, _ = setup_application()
    if UserValidator.validate_email('user@example.com'):
        return user_service.create_user('john_doe', 'user@example.com')
    return None


def process_order_workflow():
    """Process order workflow - multiple levels of calls."""
    # Level 4: process_order_workflow -> setup_application -> OrderProcessor -> 
    #          process_new_order -> create_order -> insert
    _, _, order_processor, _, _ = setup_application()
    return order_processor.process_new_order(1, [{'item': 'product1', 'qty': 2}])


def main():
    """Main application entry point."""
    user_service, order_service, order_processor, data_manager, db = setup_application()
    
    # Level 2: main -> create_user -> insert
    if UserValidator.validate_email('user@example.com'):
        user = user_service.create_user('john_doe', 'user@example.com')
        print(f"Created user: {user}")
    
    # Level 3: main -> create_sample_user -> create_user -> insert
    sample_user = create_sample_user()
    if sample_user:
        print(f"Created sample user: {sample_user}")
    
    # Level 2: main -> save_user_data -> create_user -> insert
    saved_user = data_manager.save_user_data('jane_doe', 'jane@example.com')
    print(f"Saved user via DataManager: {saved_user}")
    
    # Level 3: main -> create_user_with_audit -> create_user -> insert
    #          main -> create_user_with_audit -> save_audit_log -> insert
    user_with_audit = data_manager.create_user_with_audit('bob_smith', 'bob@example.com')
    print(f"Created user with audit: {user_with_audit}")
    
    # Level 3: main -> create_user_wrapper -> create_user -> insert
    wrapped_user = create_user_wrapper(db, 'alice_wonder', 'alice@example.com')
    print(f"Created user via wrapper: {wrapped_user}")
    
    # Level 2: main -> process_new_order -> create_order -> insert
    order = order_processor.process_new_order(1, [{'item': 'product1', 'qty': 1}])
    print(f"Processed order: {order}")
    
    # Level 3: main -> process_order_with_validation -> create_order_with_validation -> 
    #          create_order -> insert
    validated_order = order_processor.process_order_with_validation(
        1, [{'item': 'product2', 'qty': 3}]
    )
    if validated_order:
        print(f"Processed validated order: {validated_order}")
    
    # Level 1: main -> insert (direct)
    log_id = db.insert('activity_logs', {'action': 'main_executed', 'timestamp': 'now()'})
    print(f"Created activity log: {log_id}")
    
    # Level 1: main -> bulk_user_operations -> insert (multiple direct calls)
    bulk_users = bulk_user_operations(db, [
        {'username': 'user1', 'email': 'user1@example.com'},
        {'username': 'user2', 'email': 'user2@example.com'}
    ])
    print(f"Bulk created users: {bulk_users}")
    
    # Retrieve user
    user = user_service.get_user(1)
    if user:
        print(f"Retrieved user: {user}")
    
    # Update user
    user_service.update_user(1, {'status': 'inactive'})
    
    # List all users
    users = user_service.list_users()
    print(f"Total users: {len(users)}")


if __name__ == '__main__':
    main()

