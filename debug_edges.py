"""
Debug script to see what edges are being created and why they might fail.
"""
from code_analyzer import CodeAnalyzer
from collections import defaultdict

# Analyze the code
analyzer = CodeAnalyzer()
analyzer.analyze_directory('examples/')

nodes = analyzer.get_nodes()
edges = analyzer.get_edges()

# Get all node names
node_names = {node['name'] for node in nodes}
file_paths = {node['file_path'] for node in nodes}

print("="*60)
print("EDGE ANALYSIS")
print("="*60)
print(f"\nTotal nodes: {len(nodes)}")
print(f"Total edges found: {len(edges)}\n")

# Categorize edges
edges_by_type = defaultdict(list)
for edge in edges:
    edges_by_type[edge['relationship_type']].append(edge)

print("Edges by type:")
for edge_type, edge_list in edges_by_type.items():
    print(f"  {edge_type}: {len(edge_list)}")

# Check which edges can be created (both source and target exist)
print("\n" + "="*60)
print("EDGE VALIDATION")
print("="*60)

valid_edges = []
invalid_edges = []

for edge in edges:
    source = edge['source']
    target = edge['target']
    
    # Check if source exists
    source_exists = (source in node_names) or (source in file_paths)
    
    # Check if target exists
    target_exists = (target in node_names) or (target in file_paths)
    
    if source_exists and target_exists:
        valid_edges.append(edge)
    else:
        invalid_edges.append((edge, source_exists, target_exists))

print(f"\nValid edges (both source and target exist): {len(valid_edges)}")
print(f"Invalid edges (missing source or target): {len(invalid_edges)}\n")

print("\nSample invalid edges:")
for edge, source_ok, target_ok in invalid_edges[:10]:
    print(f"  {edge['relationship_type']}: {edge['source']} -> {edge['target']}")
    print(f"    Source exists: {source_ok}, Target exists: {target_ok}")

print("\n" + "="*60)
print("NODE NAMES (first 20):")
print("="*60)
for i, node in enumerate(nodes[:20]):
    print(f"  {node['type']}: {node['name']}")

print("\n" + "="*60)
print("VALID EDGES (that can be created):")
print("="*60)
for edge in valid_edges[:10]:
    print(f"  {edge['relationship_type']}: {edge['source']} -> {edge['target']}")




