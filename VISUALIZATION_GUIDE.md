# Impact Analyzer - Visualization Guide

This guide provides ready-to-use Cypher queries for visualizing and analyzing your code graph in Neo4j Browser.

## Quick Start

1. Open Neo4j Browser at: `http://localhost:7474`
2. Login with your credentials
3. Copy and paste any query below
4. Click the play button to execute

---

## 🎯 Essential Visualization Queries

### 1. View All Nodes and Relationships (Complete Graph)
**What it shows:** Full graph visualization of your codebase
```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50
```
**Use this first** to see the overall structure!

### 2. Find What Calls a Specific Method
**What it shows:** All code that calls `DatabaseConnection.insert`
```cypher
MATCH (caller)-[r:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name as caller,
       target.name as called_function,
       r.file_path as file,
       r.line_number as line
```

### 3. Find All Methods Called by a Function
**What it shows:** What `UserService.create_user` calls
```cypher
MATCH (caller {name: 'UserService.create_user'})-[r:CALLS]->(target)
RETURN caller.name as caller,
       target.name as called_function,
       target.type as target_type,
       r.file_path as file
ORDER BY target.name
```

### 4. Visualize Function Call Network
**What it shows:** Graph view of a function and its connections
```cypher
MATCH path = (start {name: 'UserService.create_user'})-[*1..2]-(connected)
RETURN path
```
**Visual mode:** Click the "Code" icon on the left to see graph visualization!

### 5. Complete Impact Analysis (Multi-level)
**What it shows:** All nodes impacted by a function (transitive dependencies)
```cypher
MATCH path = (start {name: 'UserService.create_user'})-[*1..3]->(target)
RETURN DISTINCT target.name as impacted_node,
       target.type as node_type,
       length(path) as depth
ORDER BY depth, target.name
```

---

## 📊 Impact Analysis Workflow

### Scenario: "What happens if I change `DatabaseConnection.insert`?"

**Step 1: Find Direct Callers**
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name as impacted_function,
       caller.type as caller_type,
       caller.file_path as file
```

**Step 2: Find All Impacted Code (Multi-level)**
```cypher
MATCH path = (caller)-[*1..3]->(target {name: 'DatabaseConnection.insert'})
RETURN DISTINCT caller.name as impacted_code,
       length(path) as depth
ORDER BY depth, caller.name
```

**Step 3: Find Affected Files**
```cypher
MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN DISTINCT caller.file_path as affected_files
```

**Step 4: Visualize Impact Graph**
```cypher
MATCH path = (caller)-[*1..2]->(target {name: 'DatabaseConnection.insert'})
RETURN path
```

---

## 🔍 Code Structure Queries

### Find All Classes
```cypher
MATCH (n:Class)
RETURN n.name as class_name, 
       n.file_path as file, 
       n.line_number as line
ORDER BY n.name
```

### Find All Methods in a Class
```cypher
MATCH (m:Method)
WHERE m.name STARTS WITH 'UserService.'
RETURN m.name as method,
       m.file_path as file,
       m.line_number as line
ORDER BY m.line_number
```

### Find Classes with Their Methods
```cypher
MATCH (c:Class)
OPTIONAL MATCH (m:Method)
WHERE m.name STARTS WITH c.name + '.'
RETURN c.name as class,
       collect(m.name) as methods
ORDER BY c.name
```

### Find All Functions in a File
```cypher
MATCH (n)
WHERE n.file_path = 'examples/user_service.py'
  AND (n:Function OR n:Method OR n:Class)
RETURN n.type as type,
       n.name as name,
       n.line_number as line
ORDER BY n.line_number
```

---

## 🔗 Dependency Analysis

### Find All Imports
```cypher
MATCH (file:File)-[r:IMPORTS]->(imported)
RETURN file.name as file,
       imported.name as imported_module,
       r.line_number as line
ORDER BY file.name
```

### Visualize File Dependencies
```cypher
MATCH (file1:File)-[r:IMPORTS]->(file2:File)
RETURN file1, r, file2
```

### Find Dependencies of a Class
```cypher
MATCH (class:Class {name: 'UserService'})
MATCH path = (class)-[*1..2]->(dependency)
RETURN DISTINCT dependency.name as dependency,
       dependency.type as type,
       length(path) as depth
ORDER BY depth, dependency.name
```

### Find Shared Dependencies
```cypher
MATCH (file:File)-[:IMPORTS]->(shared)
WITH shared, collect(DISTINCT file.name) as files
WHERE size(files) > 1
RETURN shared.name as shared_dependency,
       files as used_by_files,
       size(files) as file_count
ORDER BY file_count DESC
```

---

## 📈 Statistics & Metrics

### Count Nodes by Type
```cypher
MATCH (n)
RETURN labels(n)[0] as node_type,
       count(n) as count
ORDER BY count DESC
```

### Count Relationships by Type
```cypher
MATCH ()-[r]->()
RETURN type(r) as relationship_type,
       count(r) as count
ORDER BY count DESC
```

### Find Most Called Methods
```cypher
MATCH (caller)-[:CALLS]->(target:Method)
RETURN target.name as method,
       count(caller) as call_count,
       collect(DISTINCT caller.name) as callers
ORDER BY call_count DESC
LIMIT 10
```

### Find Methods with Most Dependencies
```cypher
MATCH (caller:Method)-[:CALLS]->(target)
RETURN caller.name as function,
       count(target) as dependency_count,
       collect(DISTINCT target.name) as dependencies
ORDER BY dependency_count DESC
LIMIT 10
```

### Functions per File
```cypher
MATCH (n)
WHERE n:Function OR n:Method
RETURN n.file_path as file,
       count(n) as function_count
ORDER BY function_count DESC
```

---

## 🎨 Visual Graph Queries

### Visualize Complete Class Network
```cypher
MATCH (class:Class {name: 'UserService'})
MATCH path = (class)-[*1..3]-(related)
RETURN path
```

### Visualize Inheritance Hierarchy
```cypher
MATCH path = (child:Class)-[:INHERITS*]->(parent:Class)
RETURN path
```

### Visualize Call Graph for a Class
```cypher
MATCH (class:Class {name: 'UserService'})
MATCH (caller)-[r:CALLS]->(target)
WHERE caller.name STARTS WITH class.name + '.'
   OR target.name STARTS WITH class.name + '.'
RETURN caller, r, target
```

---

## 🔎 Advanced Analysis

### Find Functions with No Callers (Dead Code)
```cypher
MATCH (n:Function)
WHERE NOT ()-[:CALLS]->(n)
RETURN n.name as unused_function,
       n.file_path as file
```

### Find Functions with No Dependencies
```cypher
MATCH (n:Function)
WHERE NOT (n)-[:CALLS]->()
RETURN n.name as function_name,
       n.file_path as file
```

### Find Longest Call Chains
```cypher
MATCH path = (start)-[:CALLS*]->(end)
WHERE NOT (end)-[:CALLS]->()
WITH path, length(path) as depth
ORDER BY depth DESC
LIMIT 10
RETURN [node in nodes(path) | node.name] as call_chain,
       depth
```

---

## 🛠️ Troubleshooting

### If a query returns no results:

1. **Check if the node name exists:**
   ```cypher
   MATCH (n)
   WHERE n.name CONTAINS 'insert'
   RETURN n.name, n.type
   ```

2. **Check all method names:**
   ```cypher
   MATCH (n:Method)
   RETURN n.name
   ORDER BY n.name
   ```

3. **Find exact name matches:**
   ```cypher
   MATCH (n)
   RETURN n.name
   ORDER BY n.name
   ```

### Common Issues:

- **Method name mismatch:** Method names are stored as `Class.method`, not just `method`
- **Case sensitivity:** Node names are case-sensitive
- **Use STARTS WITH:** For partial matches, use `WHERE n.name STARTS WITH 'Class.'`

---

## 📝 Query Tips

1. **Use LIMIT** for large graphs: Add `LIMIT 50` to prevent browser slowdown
2. **Use DISTINCT** when paths create duplicates
3. **Variable length paths:** `[*1..3]` means 1 to 3 hops
4. **Visual mode:** Click "Code" icon on left sidebar to see graph visualization
5. **Table mode:** Click "Table" icon to see tabular results

---

## 🎯 Example Analysis Session

### Step 1: Explore the Graph
```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 25
```

### Step 2: Find a Specific Function
```cypher
MATCH (n:Method)
WHERE n.name CONTAINS 'create_user'
RETURN n.name, n.file_path
```

### Step 3: Analyze Its Impact
```cypher
MATCH path = (start {name: 'UserService.create_user'})-[*1..3]->(target)
RETURN DISTINCT target.name as impacted,
       length(path) as depth
ORDER BY depth
```

### Step 4: Visualize
```cypher
MATCH path = (start {name: 'UserService.create_user'})-[*1..2]-(connected)
RETURN path
```

---

## 🚀 Quick Reference

| Goal | Query Pattern |
|------|--------------|
| Find callers | `(caller)-[:CALLS]->(target)` |
| Find callees | `(caller)-[:CALLS]->(target)` |
| Find imports | `(file)-[:IMPORTS]->(module)` |
| Multi-level | `[*1..3]` |
| Visualize | `RETURN path` |
| Count | `count(r)` |

---

Happy analyzing! 🎉

For more queries, check `visualize_queries.py` or run:
```bash
python3 visualize_queries.py
```




