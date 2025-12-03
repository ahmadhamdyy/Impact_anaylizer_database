# Impact Analyzer - Code Explanation

## Overview

The Impact Analyzer is a Python tool that analyzes your codebase and creates a graph database in Neo4j to visualize code dependencies and relationships. This document explains how the code works.

---

## Architecture

The project consists of three main components:

1. **`main.py`** - Entry point and orchestration
2. **`code_analyzer.py`** - Parses Python code using AST (Abstract Syntax Tree)
3. **`neo4j_connector.py`** - Interacts with Neo4j database

```
┌─────────────┐
│   main.py   │  ← Orchestrates the entire process
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────────┐  ┌───────────────┐
│ code_analyzer│  │neo4j_connector│
│    .py       │  │     .py       │
└──────────────┘  └───────────────┘
       │                 │
       │  Nodes & Edges  │
       └────────>────────┘
                 │
                 ▼
            Neo4j Database
```

---

## 1. Main Module (`main.py`)

### Purpose
The main entry point that coordinates the entire analysis process.

### How It Works

**Step 1: Parse Command Line Arguments**
```python
parser = argparse.ArgumentParser(...)
parser.add_argument('--path', ...)      # Path to analyze
parser.add_argument('--uri', ...)        # Neo4j connection URI
parser.add_argument('--user', ...)       # Neo4j username
parser.add_argument('--password', ...)   # Neo4j password
parser.add_argument('--clear', ...)      # Clear DB flag
```
- Uses Python's `argparse` to handle command-line inputs
- Provides defaults for Neo4j connection (localhost:7687, user: neo4j)

**Step 2: Initialize Code Analyzer**
```python
analyzer = CodeAnalyzer()
```
- Creates an instance of the `CodeAnalyzer` class
- This will collect nodes and edges as it analyzes code

**Step 3: Analyze Code**
```python
if os.path.isfile(args.path):
    analyzer.analyze_file(args.path)      # Single file
else:
    analyzer.analyze_directory(args.path) # Entire directory
```
- Determines if input is a file or directory
- Calls appropriate analysis method

**Step 4: Connect to Neo4j**
```python
connector = Neo4jConnector(args.uri, args.user, args.password)
```
- Creates a connection to Neo4j database
- Tests connection to ensure it's working

**Step 5: Load Data**
```python
connector.load_graph_data(nodes, edges)
```
- Takes the extracted nodes and edges
- Creates them in Neo4j database

---

## 2. Code Analyzer Module (`code_analyzer.py`)

### Purpose
Parses Python source code and extracts:
- **Nodes**: Classes, Functions, Methods, Files
- **Edges**: CALLS, IMPORTS, INHERITS relationships

### Key Concepts

#### Abstract Syntax Tree (AST)
Python's `ast` module parses code into a tree structure without executing it. This allows us to analyze code structure statically.

**Example:**
```python
def hello():
    print("world")
```

This becomes:
```
FunctionDef
  ├── name: "hello"
  └── body: [Call]
           └── func: Name("print")
```

### Components

#### A. CodeAnalyzer Class

**Data Structures:**
```python
self.nodes = []  # List of node dictionaries
self.edges = []  # List of edge dictionaries
self.file_imports = {}  # Track imports per file
```

**Key Methods:**

1. **`analyze_file(file_path)`**
   - Reads Python file
   - Parses it into an AST tree
   - Creates a `CodeVisitor` to walk the tree
   - Visitor extracts nodes and edges

2. **`analyze_directory(directory_path)`**
   - Recursively finds all `.py` files
   - Skips `__pycache__` and `venv` directories
   - Analyzes each file

3. **`add_node()` / `add_edge()`**
   - Simple data collection methods
   - Store information about code elements

#### B. CodeVisitor Class

This is the heart of code analysis. It inherits from `ast.NodeVisitor`, which uses the **Visitor Pattern** to traverse the AST.

**How Visitor Pattern Works:**
- AST has different node types (ClassDef, FunctionDef, Call, etc.)
- Visitor has methods like `visit_ClassDef()`, `visit_FunctionDef()`
- When walking the tree, Python automatically calls the appropriate `visit_*` method for each node

**State Tracking:**
```python
self.current_class = None      # Track which class we're in
self.current_function = None   # Track which function we're in
self.imports = {}              # Map imported names to their modules
```

This allows us to build fully qualified names like `UserService.create_user` instead of just `create_user`.

### Visitor Methods Explained

#### 1. `visit_Import(node)` - Handles `import` statements

```python
import sqlite3
import typing
```

**What it does:**
- Extracts module names
- Tracks them in `self.imports` dictionary
- Creates an IMPORTS edge from file → module

**Example:**
```python
import sqlite3
# Creates edge: examples/database.py → sqlite3 (IMPORTS)
```

#### 2. `visit_ImportFrom(node)` - Handles `from ... import` statements

```python
from examples.database import DatabaseConnection
```

**What it does:**
- Extracts both module and imported name
- Creates edges for both:
  - Full path: `examples.database.DatabaseConnection`
  - Short name: `DatabaseConnection`
- This helps match edges even if names are used differently

#### 3. `visit_ClassDef(node)` - Handles class definitions

```python
class UserService:
    def __init__(self):
        pass
```

**What it does:**
1. Creates a Class node
2. Tracks inheritance (base classes)
3. Sets `self.current_class` to track context
4. Creates INHERITS edges if class inherits from another
5. Visits child nodes (methods, nested classes)

**Context Tracking:**
```python
previous_class = self.current_class
self.current_class = "UserService"
# ... visit children ...
self.current_class = previous_class  # Restore
```
This ensures nested structures are handled correctly.

#### 4. `visit_FunctionDef(node)` - Handles function/method definitions

```python
def create_user(self, username: str):
    pass
```

**What it does:**
1. Determines if it's a Method (inside class) or Function (standalone)
2. Builds fully qualified name:
   - If in class: `UserService.create_user`
   - If standalone: `create_user`
   - If nested: `outer_function.inner_function`
3. Creates node with metadata (arguments, line number)
4. Tracks context for nested functions

**Example:**
```python
class UserService:
    def create_user(self):  # → "UserService.create_user"
        pass

def standalone():  # → "standalone"
    pass
```

#### 5. `visit_Call(node)` - Handles function/method calls

```python
result = db.insert('users', data)  # Method call
user = UserService()                # Class instantiation
```

**What it does:**
1. Identifies the source (which function/method is making the call)
2. Extracts the target (what's being called)
3. Resolves imported names (e.g., `DatabaseConnection` from imports)
4. Creates CALLS edge

**Two Types of Calls:**

**Direct function call:**
```python
setup_application()  # → CALLS: main → setup_application
```

**Method call:**
```python
self.db.insert(...)  # → CALLS: UserService.create_user → insert
```

**Note:** Method calls like `self.db.insert()` are challenging because:
- We need to know `self.db` is a `DatabaseConnection` instance
- This requires type inference (not implemented yet)
- Currently, we create edges using just the method name (`insert`)

### Edge Creation Logic

Edges are created with:
- **source**: The caller (function/method/file)
- **target**: The callee (function/method/class/module)
- **relationship_type**: CALLS, IMPORTS, or INHERITS
- **file_path**: Where this relationship exists
- **line_number**: Specific line in the code

---

## 3. Neo4j Connector Module (`neo4j_connector.py`)

### Purpose
Manages all interactions with Neo4j graph database.

### Key Concepts

#### Neo4j Graph Database
- **Nodes**: Entities (Classes, Functions, Files)
- **Relationships**: Connections between nodes (CALLS, IMPORTS)
- **Labels**: Types of nodes (Class, Function, Method, File)
- **Properties**: Attributes on nodes/relationships (name, file_path, line_number)

### Components

#### A. Connection Management

```python
def __init__(self, uri, user, password):
    self.driver = GraphDatabase.driver(uri, auth=(user, password))
```
- Creates a driver instance
- Driver handles connection pooling and transactions

#### B. Node Creation

```python
def create_node(node_type, name, file_path, line_number, metadata):
    query = f"""
    MERGE (n:{node_type} {{name: $name}})
    SET n.file_path = $file_path,
        n.line_number = $line_number,
        n.type = $node_type
    """
```

**Cypher Query Explanation:**
- `MERGE`: Creates node if it doesn't exist, or matches existing one
- `{node_type}`: Dynamic label (Class, Function, Method, File)
- `{name: $name}`: Property matching by name
- `SET`: Updates/creates properties

**Example:**
```cypher
MERGE (n:Class {name: "UserService"})
SET n.file_path = "examples/user_service.py",
    n.line_number = 10
```

This creates a node with label `Class` and properties for name, file path, and line number.

#### C. Edge Creation

```python
def create_edge(source, target, relationship_type, file_path, line_number):
    query = f"""
    MATCH (source), (target)
    WHERE source.name = $source AND target.name = $target
    MERGE (source)-[r:{relationship_type}]->(target)
    SET r.file_path = $file_path
    """
```

**Cypher Query Explanation:**
- `MATCH (source), (target)`: Finds both nodes
- `WHERE`: Filters by name property
- `MERGE ...-[r:RELATIONSHIP]->`: Creates relationship if it doesn't exist
- `SET`: Adds properties to relationship

**Example:**
```cypher
MATCH (source), (target)
WHERE source.name = "UserService.create_user" 
  AND target.name = "DatabaseConnection.insert"
MERGE (source)-[r:CALLS]->(target)
SET r.file_path = "examples/user_service.py"
```

#### D. Data Loading with Filtering

The `load_graph_data()` method is crucial. It:

1. **Creates File Nodes**
   - Every file gets a File node
   - Allows edges from files to imported modules

2. **Creates All Code Nodes**
   - Classes, Functions, Methods

3. **Filters Edges**
   ```python
   # Only create edges where both source AND target exist
   source_exists = (source in node_names) or (source in file_paths)
   target_exists = (target in node_names) or (target in file_paths)
   ```

4. **Filters Out Built-ins**
   ```python
   builtin_modules = {'typing', 'sqlite3', 'smtplib', ...}
   builtin_functions = {'join', 'split', 'keys', ...}
   ```
   - Prevents creating edges to Python built-in functions
   - Keeps graph focused on YOUR code

5. **Creates Valid Edges**
   - Only creates edges that pass all filters
   - Uses try/except to handle any edge creation failures

**Why Filtering is Important:**
- Your code calls `list.join()` → This is a built-in, not your code
- Your code imports `sqlite3` → This is external, not in your graph
- We only want edges between YOUR code elements

#### E. Statistics and Queries

**`get_statistics()`**: Runs Cypher queries to count:
- Nodes by type (Class, Function, Method, File)
- Edges by type (CALLS, IMPORTS, INHERITS)

**`find_impact(node_name, depth)`**: Impact analysis query
```cypher
MATCH path = (start {name: $node_name})-[*1..2]->(target)
RETURN target.name, length(path) as depth
```
- Uses variable-length paths `[*1..2]` to find all nodes reachable within 2 steps
- Returns impacted nodes and their distance

---

## Execution Flow

Here's the complete flow when you run the tool:

```
1. User runs: python main.py --path examples/ --clear

2. main.py:
   ├─ Parses arguments
   ├─ Creates CodeAnalyzer()
   └─ Calls analyzer.analyze_directory('examples/')

3. CodeAnalyzer:
   ├─ Finds all .py files
   ├─ For each file:
   │   ├─ Reads file content
   │   ├─ Parses AST: ast.parse(content)
   │   ├─ Creates CodeVisitor
   │   └─ visitor.visit(tree)
   │       ├─ Visits each AST node
   │       ├─ visit_ClassDef() → Creates Class node
   │       ├─ visit_FunctionDef() → Creates Function/Method node
   │       ├─ visit_Import() → Creates IMPORTS edge
   │       └─ visit_Call() → Creates CALLS edge
   └─ Returns nodes and edges lists

4. main.py:
   ├─ Creates Neo4jConnector()
   ├─ Connects to Neo4j
   └─ Calls connector.load_graph_data(nodes, edges)

5. Neo4jConnector:
   ├─ Creates File nodes
   ├─ Creates all code nodes (Class, Function, Method)
   ├─ Filters edges (removes built-ins, external refs)
   └─ Creates valid edges in Neo4j

6. Done! Graph is in Neo4j
```

---

## Key Design Decisions

### 1. Why AST Instead of Regex?
- AST is accurate and understands Python syntax
- Regex would miss edge cases and be error-prone
- AST provides structured data (line numbers, contexts)

### 2. Why Visitor Pattern?
- Clean separation: AST structure vs. analysis logic
- Easy to extend: add new `visit_*` methods
- Handles nested structures automatically

### 3. Why Filter Edges?
- Most edges reference external/built-in code
- Graph would be cluttered with irrelevant connections
- Focus on YOUR codebase relationships

### 4. Why Fully Qualified Names?
- `create_user` could exist in multiple classes
- `UserService.create_user` is unique
- Enables accurate impact analysis

---

## Limitations & Future Improvements

### Current Limitations:
1. **Type Inference**: Can't resolve `self.db.insert()` → `DatabaseConnection.insert`
   - Would need to track variable types through assignments
   - Requires analyzing `__init__` methods

2. **External Dependencies**: Can't analyze imported modules
   - Only analyzes code in the specified path
   - Could add support for analyzing installed packages

3. **Method Resolution**: Method calls on objects are partially handled
   - `self.db.insert()` creates edge to `insert`, but not `DatabaseConnection.insert`

### Potential Improvements:
1. Add type inference to resolve method calls
2. Support for decorators and generators
3. Analyze call arguments to understand data flow
4. Add support for other languages (JavaScript, Java, etc.)
5. Incremental updates (only re-analyze changed files)

---

## Example: Tracing a Code Path

Let's trace how `UserService.create_user()` is analyzed:

```python
# In user_service.py
from examples.database import DatabaseConnection

class UserService:
    def create_user(self, username: str):
        user_id = self.db.insert('users', user_data)
```

**Step 1: Import Analysis**
- `visit_ImportFrom()` creates:
  - Edge: `examples/user_service.py` → `examples.database.DatabaseConnection` (IMPORTS)
  - Edge: `examples/user_service.py` → `DatabaseConnection` (IMPORTS)
  - Stores in `self.imports`: `{'DatabaseConnection': 'examples.database.DatabaseConnection'}`

**Step 2: Class Analysis**
- `visit_ClassDef()` creates:
  - Node: `Class` with name `"UserService"`
  - Sets `self.current_class = "UserService"`

**Step 3: Method Analysis**
- `visit_FunctionDef()` creates:
  - Node: `Method` with name `"UserService.create_user"`
  - Sets `self.current_function = "UserService.create_user"`

**Step 4: Call Analysis**
- `visit_Call()` for `self.db.insert()`:
  - Source: `"UserService.create_user"`
  - Target: `"insert"` (method name extracted)
  - Creates edge: `UserService.create_user` → `insert` (CALLS)

**Step 5: Neo4j Creation**
- Creates node: `(:Method {name: "UserService.create_user"})`
- Creates node: `(:Method {name: "DatabaseConnection.insert"})`
- Creates edge: `(:Method {name: "UserService.create_user"})-[:CALLS]->(:Method {name: "insert"})`
  - But wait! The target name is just `"insert"`, which won't match `"DatabaseConnection.insert"`
  - This is why we currently only get 10 edges instead of more

---

## Summary

The Impact Analyzer works by:
1. **Parsing** Python code into an AST
2. **Walking** the AST tree with a visitor to extract structure
3. **Tracking** context (current class/function) to build qualified names
4. **Creating** nodes and edges representing code structure
5. **Filtering** out external/built-in references
6. **Loading** into Neo4j as a graph database

The graph enables you to:
- Visualize code dependencies
- Find what code calls what
- Understand module relationships
- Perform impact analysis (what breaks if I change X?)

This is a powerful foundation for code analysis and understanding large codebases!

