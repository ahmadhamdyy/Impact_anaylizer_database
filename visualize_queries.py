"""
Visualization Queries Helper
Provides ready-to-use Cypher queries for impact analysis visualization.
"""

# Ready-to-use Cypher queries for Neo4j Browser

QUERIES = {
    "1. Find what calls a method": """
        MATCH (caller)-[r:CALLS]->(target {name: 'DatabaseConnection.insert'})
        RETURN caller.name as caller,
               target.name as called_function,
               r.file_path as file,
               r.line_number as line
    """,
    
    "2. Find all methods called by a function": """
        MATCH (caller {name: 'UserService.create_user'})-[r:CALLS]->(target)
        RETURN caller.name as caller,
               target.name as called_function,
               target.type as target_type,
               r.file_path as file
        ORDER BY target.name
    """,
    
    "3. Visualize function call network": """
        MATCH path = (start {name: 'UserService.create_user'})-[*1..2]-(connected)
        RETURN path
    """,
    
    "4. Find all dependencies of a class": """
        MATCH (class:Class {name: 'UserService'})
        MATCH path = (class)-[*1..2]->(dependency)
        RETURN DISTINCT dependency.name as dependency,
               dependency.type as type,
               length(path) as depth
        ORDER BY depth, dependency.name
    """,
    
    "5. Find what would break if you delete a method": """
        MATCH (caller)-[:CALLS]->(target {name: 'DatabaseConnection.insert'})
        RETURN DISTINCT caller.name as would_break,
               caller.type as caller_type,
               caller.file_path as file
        ORDER BY caller.name
    """,
    
    "6. Visualize complete class network": """
        MATCH (class:Class {name: 'UserService'})
        MATCH path = (class)-[*1..3]-(related)
        RETURN path
    """,
    
    "7. Find all imports in a file": """
        MATCH (file:File {name: 'examples/user_service.py'})-[r:IMPORTS]->(imported)
        RETURN file.name as file,
               imported.name as imported_module,
               r.line_number as line
    """,
    
    "8. Visualize file dependencies": """
        MATCH (file1:File)-[r:IMPORTS]->(file2:File)
        RETURN file1, r, file2
    """,
    
    "9. Find methods in a class": """
        MATCH (m:Method)
        WHERE m.name STARTS WITH 'UserService.'
        RETURN m.name as method,
               m.file_path as file,
               m.line_number as line
        ORDER BY m.line_number
    """,
    
    "10. Complete impact analysis (multi-level)": """
        MATCH path = (start {name: 'UserService.create_user'})-[*1..3]->(target)
        RETURN DISTINCT target.name as impacted_node,
               target.type as node_type,
               length(path) as depth,
               relationships(path) as relationships
        ORDER BY depth, target.name
    """,
    
    "11. Find most called methods": """
        MATCH (caller)-[:CALLS]->(target:Method)
        RETURN target.name as method,
               count(caller) as call_count,
               collect(DISTINCT caller.name) as callers
        ORDER BY call_count DESC
        LIMIT 10
    """,
    
    "12. Visualize all relationships": """
        MATCH (n)-[r]->(m)
        RETURN n, r, m
        LIMIT 50
    """,
    
    "13. Find classes with their methods": """
        MATCH (c:Class)
        OPTIONAL MATCH (m:Method)
        WHERE m.name STARTS WITH c.name + '.'
        RETURN c.name as class,
               collect(m.name) as methods
        ORDER BY c.name
    """,
    
    "14. Visualize inheritance hierarchy": """
        MATCH path = (child:Class)-[:INHERITS*]->(parent:Class)
        RETURN path
    """,
    
    "15. Find all nodes of a specific type": """
        MATCH (n:Method)
        RETURN n.name as method_name,
               n.file_path as file,
               n.line_number as line
        ORDER BY n.name
    """
}


def print_query(name: str, query: str):
    """Print a formatted query."""
    print(f"\n{'='*60}")
    print(f"Query: {name}")
    print('='*60)
    print(query.strip())
    print('='*60)


def list_all_queries():
    """List all available queries."""
    print("\n" + "="*60)
    print("AVAILABLE VISUALIZATION QUERIES")
    print("="*60)
    for i, name in enumerate(QUERIES.keys(), 1):
        print(f"{i}. {name}")
    print("="*60)


def get_query(name: str) -> str:
    """Get a specific query by name."""
    return QUERIES.get(name, "")


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        query_name = sys.argv[1]
        if query_name in QUERIES:
            print_query(query_name, QUERIES[query_name])
        else:
            print(f"Query '{query_name}' not found.")
            list_all_queries()
    else:
        list_all_queries()
        print("\nUsage: python visualize_queries.py <query_name>")
        print("\nExample: python visualize_queries.py '1. Find what calls a method'")




