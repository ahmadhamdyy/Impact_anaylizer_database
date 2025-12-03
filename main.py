"""
Main Application
Entry point for the Impact Analyzer tool.
"""
import argparse
import os
from code_analyzer import CodeAnalyzer
from neo4j_connector import Neo4jConnector


def main():
    """Main function to run the impact analyzer."""
    parser = argparse.ArgumentParser(
        description='Impact Analyzer - Build a graph database from code for impact analysis'
    )
    parser.add_argument(
        '--path',
        type=str,
        required=True,
        help='Path to Python code file or directory to analyze'
    )
    parser.add_argument(
        '--uri',
        type=str,
        default='bolt://localhost:7687',
        help='Neo4j database URI (default: bolt://localhost:7687)'
    )
    parser.add_argument(
        '--user',
        type=str,
        default='neo4j',
        help='Neo4j username (default: neo4j)'
    )
    parser.add_argument(
        '--password',
        type=str,
        default='password',
        help='Neo4j password (default: password)'
    )
    parser.add_argument(
        '--clear',
        action='store_true',
        help='Clear existing database before loading new data'
    )
    
    args = parser.parse_args()
    
    # Validate path
    if not os.path.exists(args.path):
        print(f"Error: Path '{args.path}' does not exist.")
        return
    
    print("="*60)
    print("IMPACT ANALYZER - Code to Graph Database")
    print("="*60)
    
    # Initialize analyzer
    print("\n[1/4] Initializing code analyzer...")
    analyzer = CodeAnalyzer()
    
    # Analyze code
    print(f"\n[2/4] Analyzing code at: {args.path}")
    if os.path.isfile(args.path):
        analyzer.analyze_file(args.path)
    else:
        analyzer.analyze_directory(args.path)
    
    nodes = analyzer.get_nodes()
    edges = analyzer.get_edges()
    
    print(f"Found {len(nodes)} nodes and {len(edges)} edges")
    
    if len(nodes) == 0:
        print("No nodes found. Exiting.")
        return
    
    # Connect to Neo4j
    print(f"\n[3/4] Connecting to Neo4j at {args.uri}...")
    try:
        connector = Neo4jConnector(args.uri, args.user, args.password)
        
        # Test connection
        connector.get_node_count()
        print("Connected successfully!")
        
        # Clear database if requested
        if args.clear:
            print("\nClearing existing database...")
            connector.clear_database()
        
        # Load data into Neo4j
        print("\n[4/4] Loading graph data into Neo4j...")
        connector.load_graph_data(nodes, edges)
        
        # Display statistics
        connector.visualize_graph_summary()
        
        print("\n" + "="*60)
        print("SUCCESS! Graph database created.")
        print("="*60)
        print("\nYou can now:")
        print("1. Open Neo4j Browser at http://localhost:7474")
        print("2. Run queries like:")
        print("   - MATCH (n) RETURN n LIMIT 25")
        print("   - MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 25")
        print("   - MATCH (n:Function) RETURN n LIMIT 25")
        print("\nExample impact analysis query:")
        print("   MATCH path = (start {name: 'function_name'})-[*1..2]->(target)")
        print("   RETURN target.name as impacted_node, length(path) as depth")
        print("="*60)
        
        connector.close()
        
    except Exception as e:
        print(f"\nError connecting to Neo4j: {e}")
        print("\nMake sure Neo4j is running and credentials are correct.")
        print("You can start Neo4j with: neo4j start")
        print("Or use Neo4j Desktop to manage your database.")


if __name__ == '__main__':
    main()

