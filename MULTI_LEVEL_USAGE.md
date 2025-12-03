# Multi-Level Usage of DatabaseConnection.insert

This document shows how `DatabaseConnection.insert` is now used across multiple files and through multiple call levels.

## Summary

- **Total Nodes**: 57 (up from 35)
- **Total Edges**: 41 (up from 16)
- **CALLS Relationships**: 28
- **Files Using insert**: 5 files
- **Call Levels**: 1 to 4 levels deep

---

## Files Using DatabaseConnection.insert

1. **examples/user_service.py**
2. **examples/main_app.py**
3. **examples/order_service.py**
4. **examples/data_manager.py**
5. **examples/database.py** (where it's defined)

---

## Call Level Breakdown

### Level 1: Direct Calls
These functions/methods directly call `DatabaseConnection.insert`:

1. **UserService.create_user** (user_service.py)
   ```python
   user_id = self.db.insert('users', user_data)
   ```

2. **UserService.create_user_with_profile** (user_service.py)
   ```python
   profile_id = self.db.insert('user_profiles', {...})
   ```

3. **OrderService.create_order** (order_service.py)
   ```python
   order_id = self.db.insert('orders', order_data)
   ```

4. **OrderService.bulk_create_orders** (order_service.py)
   ```python
   order_id = self.db.insert('orders', order)
   ```

5. **DataManager.save_audit_log** (data_manager.py)
   ```python
   return self.db.insert('audit_logs', log_data)
   ```

6. **main function** (main_app.py)
   ```python
   log_id = db.insert('activity_logs', {...})
   ```

7. **bulk_user_operations** (data_manager.py)
   ```python
   user_id = db.insert('users', user)
   ```

### Level 2: One Level Indirect
These call functions that call `insert`:

1. **UserService.create_user_with_profile** → **create_user** → **insert**
2. **OrderService.create_order_with_validation** → **create_order** → **insert**
3. **OrderProcessor.process_new_order** → **create_order** → **insert**
4. **OrderProcessor.process_bulk_orders** → **bulk_create_orders** → **insert**
5. **DataManager.save_user_data** → **create_user** → **insert**
6. **DataManager.create_user_with_audit** → **create_user** → **insert**
7. **main** → **create_user** → **insert**
8. **main** → **process_new_order** → **create_order** → **insert**
9. **main** → **save_user_data** → **create_user** → **insert**

### Level 3: Two Levels Indirect
These call functions that call functions that call `insert`:

1. **OrderProcessor.process_order_with_validation** → **create_order_with_validation** → **create_order** → **insert**
2. **DataManager.create_user_with_audit** → **create_user** → **insert** (and also directly calls insert)
3. **create_user_wrapper** → **UserService.create_user** → **insert**
4. **main** → **create_sample_user** → **create_user** → **insert**
5. **main** → **create_user_with_audit** → **create_user** → **insert**
6. **main** → **create_user_wrapper** → **create_user** → **insert**
7. **main** → **process_order_with_validation** → **create_order_with_validation** → **create_order** → **insert**

### Level 4: Three Levels Indirect
These have the deepest call chains:

1. **process_order_workflow** → **setup_application** → **OrderProcessor.process_new_order** → **create_order** → **insert**
2. **create_sample_user** → **setup_application** → **UserService.create_user** → **insert**

---

## Complete Call Chain Examples

### Example 1: Simple Direct Call
```
main (main_app.py)
  └─> DatabaseConnection.insert
```

### Example 2: Two-Level Chain
```
main (main_app.py)
  └─> UserService.create_user (user_service.py)
      └─> DatabaseConnection.insert
```

### Example 3: Three-Level Chain
```
main (main_app.py)
  └─> create_user_wrapper (data_manager.py)
      └─> UserService.create_user (user_service.py)
          └─> DatabaseConnection.insert
```

### Example 4: Four-Level Chain
```
process_order_workflow (main_app.py)
  └─> setup_application (main_app.py)
      └─> OrderProcessor.process_new_order (order_service.py)
          └─> OrderService.create_order (order_service.py)
              └─> DatabaseConnection.insert
```

### Example 5: Multiple Paths from Same Function
```
DataManager.create_user_with_audit (data_manager.py)
  ├─> UserService.create_user (user_service.py)
  │   └─> DatabaseConnection.insert
  └─> DataManager.save_audit_log (data_manager.py)
      └─> DatabaseConnection.insert
```

---

## Cypher Queries to Explore

### Find All Direct Callers
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name as caller,
       caller.file_path as file
ORDER BY caller.name
```

### Find All Impacted Code (Multi-level)
```cypher
MATCH path = (caller)-[*1..4]->(target {name: 'DatabaseConnection.insert'})
RETURN DISTINCT caller.name as impacted_code,
       caller.type as caller_type,
       caller.file_path as file,
       length(path) as depth
ORDER BY depth, caller.name
```

### Find Affected Files
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN DISTINCT caller.file_path as affected_files
```

### Visualize Multi-Level Impact
```cypher
MATCH path = (caller)-[*1..4]->(target {name: 'DatabaseConnection.insert'})
RETURN path
```

### Count Usage by Level
```cypher
MATCH path = (caller)-[*1..4]->(target {name: 'DatabaseConnection.insert'})
RETURN length(path) as depth,
       count(DISTINCT caller) as callers_at_level
ORDER BY depth
```

---

## Impact Analysis Results

When you run the multi-level query, you should see:

**Level 1 (Direct):** ~7-8 callers
- UserService.create_user
- OrderService.create_order
- DataManager.save_audit_log
- main
- bulk_user_operations
- etc.

**Level 2 (Indirect):** ~9 callers
- UserService.create_user_with_profile
- OrderProcessor.process_new_order
- DataManager.save_user_data
- main (via various paths)
- etc.

**Level 3 (Two Levels Indirect):** ~7 callers
- OrderProcessor.process_order_with_validation
- create_user_wrapper
- main (via wrapper paths)
- etc.

**Level 4 (Three Levels Indirect):** ~2 callers
- process_order_workflow
- create_sample_user

**Total Impact:** ~25+ functions/methods across 5 files

---

## Files Structure

```
examples/
├── database.py              (defines DatabaseConnection.insert)
├── user_service.py          (uses insert: Level 1, 2)
├── order_service.py         (uses insert: Level 1, 2, 3)
├── data_manager.py          (uses insert: Level 1, 2, 3)
└── main_app.py             (uses insert: Level 1, 2, 3, 4)
```

---

## Testing the Queries

Run these queries in Neo4j Browser to see the multi-level impact:

1. **Quick Check - Direct Callers:**
   ```cypher
   MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
   RETURN count(caller) as direct_callers
   ```

2. **Full Impact Analysis:**
   ```cypher
   MATCH path = (caller)-[*1..4]->(target {name: 'DatabaseConnection.insert'})
   RETURN DISTINCT caller.name, length(path) as depth
   ORDER BY depth
   ```

3. **Visualize:**
   ```cypher
   MATCH path = (caller)-[*1..4]->(target {name: 'DatabaseConnection.insert'})
   RETURN path
   LIMIT 50
   ```

This now demonstrates a comprehensive multi-level, multi-file usage pattern perfect for impact analysis!




