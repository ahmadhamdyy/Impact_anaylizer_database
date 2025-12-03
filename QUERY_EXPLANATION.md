# Cypher Query Explanation - Impact Analysis Workflow

This document explains each Cypher query in the Impact Analysis Workflow for understanding what happens when you change `DatabaseConnection.insert`.

---

## Overview: What Are We Trying to Find?

When you change a method like `DatabaseConnection.insert`, you need to know:
1. **What directly calls it?** (Immediate impact)
2. **What indirectly depends on it?** (Transitive impact)
3. **Which files are affected?** (File-level impact)

---

## Step 1: Find Direct Callers

### Query:
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name
```

### Breaking It Down:

#### `MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})`
- **`MATCH`**: This is the pattern matching clause. It tells Neo4j to find nodes and relationships that match a specific pattern.
- **`(caller)`**: This is a node variable named `caller`. It represents any node that will be the source of a CALLS relationship.
- **`-[:CALLS]->`**: This specifies the relationship pattern:
  - `-` means "from a node"
  - `[:CALLS]` means "with a relationship of type CALLS"
  - `->` means "to a node"
  - So `(caller)-[:CALLS]->(target)` means: "find a caller node that has a CALLS relationship going TO a target node"
- **`(target {name: 'DatabaseConnection.insert'})`**: This is the target node with a specific property:
  - `(target)` is a node variable
  - `{name: 'DatabaseConnection.insert'}` is a property filter that matches nodes where the `name` property equals `'DatabaseConnection.insert'`

**In Plain English:** "Find all nodes that call the method named 'DatabaseConnection.insert'"

#### `RETURN caller.name`
- **`RETURN`**: This specifies what data to return from the query
- **`caller.name`**: Returns the `name` property of the `caller` nodes we found

**What It Returns:**
- A list of function/method names that directly call `DatabaseConnection.insert`
- Example results: `UserService.create_user`, `UserService.update_user`, etc.

**Visual Representation:**
```
UserService.create_user ──[:CALLS]──> DatabaseConnection.insert
UserService.update_user ──[:CALLS]──> DatabaseConnection.insert
```

---

## Step 2: Find All Impacted Code (Multi-level)

### Query:
```cypher
MATCH path = (caller)-[*1..3]->(target {name: 'DatabaseConnection.insert'})
RETURN DISTINCT caller.name as impacted_code
```

### Breaking It Down:

#### `MATCH path = (caller)-[*1..3]->(target {name: 'DatabaseConnection.insert'})`
- **`path =`**: This assigns the entire path (sequence of nodes and relationships) to a variable called `path`
- **`[*1..3]`**: This is a **variable-length path** pattern:
  - `[*]` means "any number of relationships"
  - `[1..3]` means "between 1 and 3 relationships"
  - So `[*1..3]` means: "follow the path through 1, 2, or 3 relationships"
- **`->`**: Direction is REVERSED here! We're going FROM caller TO target, which means:
  - We're finding nodes that eventually reach the target
  - This finds both direct and indirect dependencies

**In Plain English:** "Find all nodes that can reach 'DatabaseConnection.insert' through 1 to 3 relationship hops"

**Why Multi-level?**
- **Level 1 (Direct)**: `UserService.create_user` → `DatabaseConnection.insert`
- **Level 2 (Indirect)**: `main` → `UserService.create_user` → `DatabaseConnection.insert`
- **Level 3 (More Indirect)**: `setup_application` → `main` → `UserService.create_user` → `DatabaseConnection.insert`

**Visual Representation:**
```
setup_application ──[:CALLS]──> main ──[:CALLS]──> UserService.create_user ──[:CALLS]──> DatabaseConnection.insert
                                                                                ↑
                                                                    (target we're looking for)
```

#### `RETURN DISTINCT caller.name as impacted_code`
- **`DISTINCT`**: Removes duplicate results. If a node appears in multiple paths, it's only returned once.
- **`caller.name as impacted_code`**: Returns the caller's name with an alias `impacted_code` for better readability

**What It Returns:**
- All functions/methods that depend on `DatabaseConnection.insert` (directly or indirectly)
- Includes the call chain, so you can see the full dependency path

---

## Step 3: Find Files That Use It

### Query:
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN DISTINCT caller.file_path as affected_files
```

### Breaking It Down:

#### `MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})`
- Same as Step 1: Find direct callers of `DatabaseConnection.insert`

#### `RETURN DISTINCT caller.file_path as affected_files`
- **`caller.file_path`**: Returns the `file_path` property of the caller nodes
- **`DISTINCT`**: Ensures each file is only listed once, even if multiple functions in that file call the method
- **`as affected_files`**: Renames the column for clarity

**What It Returns:**
- A list of file paths that contain code calling `DatabaseConnection.insert`
- Example: `['examples/user_service.py', 'examples/main_app.py']`

**Use Case:**
- Helps you know which files to review when making changes
- Useful for coordinating with team members
- Helps estimate scope of testing needed

---

## Complete Example: Understanding the Results

Let's say you run all three queries and get:

### Step 1 Results:
```
caller.name
─────────────────────────────
UserService.create_user
UserService.update_user
UserService.delete_user
```

### Step 2 Results:
```
impacted_code
─────────────────────────────
UserService.create_user
UserService.update_user
UserService.delete_user
main
setup_application
```

### Step 3 Results:
```
affected_files
─────────────────────────────
examples/user_service.py
examples/main_app.py
```

### Interpretation:

**Direct Impact (Step 1):**
- 3 methods directly call `DatabaseConnection.insert`
- These will definitely break if you change the method signature

**Transitive Impact (Step 2):**
- 5 total functions/methods are affected
- `main` and `setup_application` are indirectly affected because they call `UserService` methods

**File Impact (Step 3):**
- 2 files need to be reviewed/tested
- You should check both files when making changes

---

## Query Patterns Explained

### Pattern 1: Direct Relationship
```cypher
(caller)-[:CALLS]->(target)
```
- **Meaning:** One hop, direct relationship
- **Use:** Find immediate dependencies

### Pattern 2: Variable-Length Path (Forward)
```cypher
(start)-[*1..3]->(end)
```
- **Meaning:** 1-3 hops in the forward direction
- **Use:** Find what `start` calls (directly or indirectly)

### Pattern 3: Variable-Length Path (Reverse)
```cypher
(caller)-[*1..3]->(target)
```
- **Meaning:** 1-3 hops in reverse direction
- **Use:** Find what eventually reaches `target` (reverse dependency)

### Pattern 4: Property Filtering
```cypher
{name: 'DatabaseConnection.insert'}
```
- **Meaning:** Match nodes where `name` property equals the value
- **Use:** Find specific nodes by property

### Pattern 5: DISTINCT
```cypher
RETURN DISTINCT caller.name
```
- **Meaning:** Remove duplicates
- **Use:** Get unique results when paths create duplicates

---

## Common Variations

### Variation 1: Include Relationship Details
```cypher
MATCH (caller)-[r:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name, r.file_path, r.line_number
```
- Returns not just the caller, but also WHERE the call happens (file and line number)

### Variation 2: Include Node Types
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name, caller.type, caller.file_path
```
- Shows what type of node is calling (Method, Function, etc.)

### Variation 3: Visualize the Path
```cypher
MATCH path = (caller)-[*1..3]->(target {name: 'DatabaseConnection.insert'})
RETURN path
```
- Returns the entire path for visualization in Neo4j Browser graph view

### Variation 4: Count Impact
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN count(DISTINCT caller) as total_callers
```
- Just counts how many callers exist (quick impact assessment)

---

## Tips for Using These Queries

1. **Start with Step 1**: Get immediate impact first
2. **Use Step 2 for scope**: Understand full impact before making changes
3. **Use Step 3 for planning**: Know which files to review/test
4. **Adjust path depth**: Change `[*1..3]` to `[*1..5]` for deeper analysis
5. **Combine with filtering**: Add `WHERE caller.file_path CONTAINS 'specific_folder'` to focus on certain areas

---

## Summary

| Query | Purpose | Pattern | Returns |
|-------|---------|---------|---------|
| Step 1 | Direct callers | `(caller)-[:CALLS]->(target)` | Immediate dependencies |
| Step 2 | All impacted code | `(caller)-[*1..3]->(target)` | Direct + indirect dependencies |
| Step 3 | Affected files | `(caller)-[:CALLS]->(target)` + `file_path` | Files that need review |

These queries work together to give you a complete picture of impact when making changes to your code!

