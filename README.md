# Impact Analyzer

A Python tool that analyzes code structure and creates a graph database in Neo4j for impact analysis. This tool helps developers understand code dependencies, relationships, and the potential impact of changes across their codebase.

## Features

- **Code Analysis**: Automatically parses Python code to extract:
  - Classes and methods
  - Functions
  - Import relationships
  - Function/method calls
  - Inheritance relationships
  
- **Graph Database**: Creates a visual graph in Neo4j showing:
  - Nodes: Classes, Functions, Methods, Files, Modules
  - Edges: CALLS, IMPORTS, INHERITS relationships
  
- **Impact Analysis**: Identify which parts of the codebase are affected by changes to specific functions or classes

## Prerequisites

1. **Python 3.7+**
2. **Neo4j Database**
   - Download and install from [neo4j.com](https://neo4j.com/download/)
   - Or use Neo4j Desktop: [neo4j.com/desktop](https://neo4j.com/desktop/)
   - Start Neo4j server (default: `bolt://localhost:7687`)

## Installation

1. Clone or navigate to this repository:
   ```bash
   cd Impact_anaylizer
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Make sure Neo4j is running:
   ```bash
   neo4j start
   # Or use Neo4j Desktop to start your database
   ```

## Configuration

By default, the tool connects to:
- **URI**: `bolt://localhost:7687`
- **Username**: `neo4j`
- **Password**: `password`

If your Neo4j instance uses different credentials, you can specify them via command-line arguments.

## Usage

### Basic Usage

Analyze a single Python file:
```bash
python main.py --path examples/user_service.py
```

Analyze an entire directory:
```bash
python main.py --path examples/
```

### Advanced Usage

Specify custom Neo4j connection:
```bash
python main.py --path examples/ \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password your_password
```

Clear existing database before loading:
```bash
python main.py --path examples/ --clear
```

### Example: Analyze the Example Code

The project includes example code in the `examples/` directory. To analyze it:

```bash
python main.py --path examples/
```

This will:
1. Parse all Python files in the `examples/` directory
2. Extract nodes (classes, functions, methods) and edges (calls, imports)
3. Load the graph structure into Neo4j
4. Display statistics about the created graph

## Viewing the Graph

### Neo4j Browser

1. Open Neo4j Browser at: `http://localhost:7474`
2. Login with your Neo4j credentials
3. Run queries to explore the graph

### Visualization Guide

For comprehensive visualization queries, see **[VISUALIZATION_GUIDE.md](VISUALIZATION_GUIDE.md)** - a complete guide with ready-to-use queries.

**Quick Start Queries:**

**View complete graph:**
```cypher
MATCH (n)-[r]->(m)
RETURN n, r, m
LIMIT 50
```

**Find what calls a method:**
```cypher
MATCH (caller)-[r:CALLS]->(target {name: 'DatabaseConnection.insert'})
RETURN caller.name as caller,
       target.name as called_function,
       r.file_path as file
```

**Visualize function network:**
```cypher
MATCH path = (start {name: 'UserService.create_user'})-[*1..2]-(connected)
RETURN path
```

**Complete impact analysis:**
```cypher
MATCH path = (start {name: 'UserService.create_user'})-[*1..3]->(target)
RETURN DISTINCT target.name as impacted_node,
       target.type as node_type,
       length(path) as depth
ORDER BY depth, target.name
```

**Get all available queries:**
```bash
python3 visualize_queries.py
```

For more detailed queries, see **VISUALIZATION_GUIDE.md**.

## Project Structure

```
Impact_anaylizer/
├── main.py                 # Main application entry point
├── code_analyzer.py        # Code parsing and analysis logic
├── neo4j_connector.py      # Neo4j database operations
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── examples/              # Example code for demonstration
    ├── user_service.py
    ├── database.py
    ├── email_sender.py
    └── main_app.py
```

## How It Works

1. **Code Parsing**: Uses Python's `ast` (Abstract Syntax Tree) module to parse Python code without executing it
2. **Node Extraction**: Identifies classes, functions, methods, and files as nodes
3. **Edge Extraction**: Identifies relationships like:
   - `CALLS`: Function A calls Function B
   - `IMPORTS`: File A imports Module B
   - `INHERITS`: Class A inherits from Class B
4. **Graph Creation**: Loads nodes and edges into Neo4j with appropriate labels and properties

## Node Types

- **File**: Python source files
- **Class**: Class definitions
- **Function**: Standalone functions
- **Method**: Methods within classes

## Relationship Types

- **CALLS**: A function/method calls another function
- **IMPORTS**: A file imports a module or class
- **INHERITS**: A class inherits from another class

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Verify Neo4j is running: `neo4j status`
2. Check the URI matches your Neo4j configuration
3. Verify username and password are correct
4. Check firewall settings if using remote Neo4j instance

### Empty Graph

If no nodes are found:
1. Verify the path contains Python files (`.py` extension)
2. Check that files are not in `__pycache__` or `venv` directories (these are automatically excluded)
3. Ensure files have valid Python syntax

### Performance

For large codebases:
- The analysis may take some time
- Consider analyzing specific directories rather than the entire codebase
- Neo4j performance depends on your hardware and database configuration

## Future Enhancements

Potential improvements:
- Support for other languages (JavaScript, Java, etc.)
- More relationship types (DEPENDS_ON, USES, etc.)
- Impact analysis queries with visualization
- Integration with CI/CD pipelines
- Change detection and incremental updates

## License

This project is provided as-is for educational and development purposes.

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

