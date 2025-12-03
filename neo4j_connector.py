"""
Neo4j Connector Module
Handles connection to Neo4j database and graph operations.
"""
from neo4j import GraphDatabase
from typing import List, Dict, Optional


class Neo4jConnector:
    """Manages connection and operations with Neo4j database."""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j database URI (e.g., 'bolt://localhost:7687')
            user: Neo4j username
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.uri = uri
        self.user = user
    
    def close(self):
        """Close the database connection."""
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships from the database."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        print("Database cleared successfully.")
    
    def create_node(self, node_type: str, name: str, file_path: str, 
                   line_number: int, metadata: Dict = None) -> None:
        """
        Create a node in Neo4j.
        
        Args:
            node_type: Type of node (Class, Function, Method, File, etc.)
            name: Name of the node
            file_path: Path to the file containing this node
            line_number: Line number in the file
            metadata: Additional metadata dictionary
        """
        with self.driver.session() as session:
            # Create node with type-specific label and properties
            query = f"""
            MERGE (n:{node_type} {{name: $name}})
            SET n.file_path = $file_path,
                n.line_number = $line_number,
                n.type = $node_type
            """
            
            params = {
                'name': name,
                'file_path': file_path,
                'line_number': line_number,
                'node_type': node_type
            }
            
            # Add metadata if provided
            if metadata:
                for key, value in metadata.items():
                    if isinstance(value, (str, int, float, bool)):
                        query += f", n.{key} = ${key}"
                        params[key] = value
                    elif isinstance(value, list):
                        query += f", n.{key} = ${key}"
                        params[key] = value
            
            session.run(query, params)
    
    def create_edge(self, source: str, target: str, relationship_type: str,
                   file_path: str, line_number: Optional[int] = None) -> None:
        """
        Create a relationship (edge) in Neo4j.
        
        Args:
            source: Source node name
            target: Target node name
            relationship_type: Type of relationship (CALLS, IMPORTS, INHERITS, etc.)
            file_path: Path to the file containing this relationship
            line_number: Line number in the file
        """
        with self.driver.session() as session:
            query = f"""
            MATCH (source), (target)
            WHERE source.name = $source AND target.name = $target
            MERGE (source)-[r:{relationship_type}]->(target)
            SET r.file_path = $file_path
            """
            
            params = {
                'source': source,
                'target': target,
                'file_path': file_path
            }
            
            if line_number is not None:
                query += ", r.line_number = $line_number"
                params['line_number'] = line_number
            
            session.run(query, params)
    
    def create_file_node(self, file_path: str) -> None:
        """Create a file node in Neo4j."""
        with self.driver.session() as session:
            query = """
            MERGE (f:File {name: $file_path})
            SET f.file_path = $file_path,
                f.type = 'File'
            """
            session.run(query, {'file_path': file_path})
    
    def load_graph_data(self, nodes: List[Dict], edges: List[Dict]) -> None:
        """
        Load all nodes and edges into Neo4j.
        
        Args:
            nodes: List of node dictionaries
            edges: List of edge dictionaries
        """
        print(f"Loading {len(nodes)} nodes and {len(edges)} edges into Neo4j...")
        
        # Build sets of valid node names and file paths for validation
        node_names = {node['name'] for node in nodes}
        file_paths = set()
        for node in nodes:
            file_paths.add(node['file_path'])
        for edge in edges:
            file_paths.add(edge['file_path'])
        
        # Create file nodes
        for file_path in file_paths:
            self.create_file_node(file_path)
        
        # Create all nodes
        for node in nodes:
            self.create_node(
                node_type=node['type'],
                name=node['name'],
                file_path=node['file_path'],
                line_number=node['line_number'],
                metadata=node.get('metadata', {})
            )
        
        # Filter edges to only include those where both source and target exist
        # Also filter out built-in Python functions and external modules
        valid_edges = []
        builtin_modules = {'typing', 'sqlite3', 'smtplib', 'email', 'os', 'pathlib', 'collections', 
                          'sys', 'json', 'datetime', 're', 'math', 'random', 'itertools'}
        builtin_functions = {'join', 'split', 'keys', 'values', 'items', 'get', 'set', 'append',
                            'extend', 'pop', 'remove', 'insert', 'sort', 'reverse', 'copy',
                            'cursor', 'connect', 'execute', 'fetchone', 'fetchall', 'commit',
                            'close', 'starttls', 'send_message', 'quit', 'isinstance', 'len',
                            'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple'}
        
        for edge in edges:
            source = edge['source']
            target = edge['target']
            
            # Check if source exists (node name or file path)
            source_exists = (source in node_names) or (source in file_paths)
            
            # Check if target exists (node name or file path)
            target_exists = (target in node_names) or (target in file_paths)
            
            # Skip edges to built-in modules/functions
            target_is_builtin = (
                target in builtin_modules or
                target in builtin_functions or
                any(target.startswith(f"{mod}.") for mod in builtin_modules) or
                target.startswith('typing.')
            )
            
            # Only create edge if both exist and target is not built-in
            if source_exists and target_exists and not target_is_builtin:
                valid_edges.append(edge)
        
        print(f"Filtered to {len(valid_edges)} valid edges (excluding external/built-in references)")
        
        # Create valid edges
        edges_created = 0
        for edge in valid_edges:
            try:
                self.create_edge(
                    source=edge['source'],
                    target=edge['target'],
                    relationship_type=edge['relationship_type'],
                    file_path=edge['file_path'],
                    line_number=edge.get('line_number')
                )
                edges_created += 1
            except Exception as e:
                # Skip edges that can't be created
                pass
        
        print(f"Successfully created {edges_created} edges")
        print("Graph data loaded successfully!")
    
    def get_node_count(self) -> int:
        """Get total number of nodes in the database."""
        with self.driver.session() as session:
            result = session.run("MATCH (n) RETURN count(n) as count")
            return result.single()['count']
    
    def get_edge_count(self) -> int:
        """Get total number of relationships in the database."""
        with self.driver.session() as session:
            result = session.run("MATCH ()-[r]->() RETURN count(r) as count")
            return result.single()['count']
    
    def get_statistics(self) -> Dict:
        """Get statistics about the graph."""
        with self.driver.session() as session:
            stats = {}
            
            # Node counts by type
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as type, count(n) as count
                ORDER BY count DESC
            """)
            stats['nodes_by_type'] = {record['type']: record['count'] 
                                     for record in result}
            
            # Relationship counts by type
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
                ORDER BY count DESC
            """)
            stats['edges_by_type'] = {record['type']: record['count'] 
                                     for record in result}
            
            stats['total_nodes'] = self.get_node_count()
            stats['total_edges'] = self.get_edge_count()
            
            return stats
    
    def find_impact(self, node_name: str, depth: int = 2) -> List[Dict]:
        """
        Find all nodes that are impacted by changes to a given node.
        
        Args:
            node_name: Name of the node to analyze
            depth: Maximum depth to traverse (default: 2)
        
        Returns:
            List of impacted nodes with their relationships
        """
        with self.driver.session() as session:
            query = f"""
            MATCH path = (start {{name: $node_name}})-[*1..{depth}]->(target)
            RETURN target.name as node, 
                   relationships(path) as relationships,
                   length(path) as depth
            ORDER BY depth, node
            """
            result = session.run(query, {'node_name': node_name})
            return [record.data() for record in result]
    
    def visualize_graph_summary(self) -> None:
        """Print a summary of the graph structure."""
        stats = self.get_statistics()
        
        print("\n" + "="*50)
        print("GRAPH DATABASE SUMMARY")
        print("="*50)
        print(f"\nTotal Nodes: {stats['total_nodes']}")
        print(f"Total Edges: {stats['total_edges']}")
        
        print("\nNodes by Type:")
        for node_type, count in stats['nodes_by_type'].items():
            print(f"  {node_type}: {count}")
        
        print("\nEdges by Type:")
        for edge_type, count in stats['edges_by_type'].items():
            print(f"  {edge_type}: {count}")
        
        print("\n" + "="*50 + "\n")

