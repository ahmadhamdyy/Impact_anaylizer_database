"""
Code Analyzer Module
Analyzes Python code to extract nodes (functions, classes, modules) and edges (dependencies, calls).
"""
import ast
import os
from typing import Dict, List, Set, Tuple
from pathlib import Path


class CodeAnalyzer:
    """Analyzes Python code to extract graph structure for impact analysis."""
    
    def __init__(self):
        self.nodes = []  # List of (type, name, file_path, line_number)
        self.edges = []  # List of (source, target, relationship_type, file_path)
        self.file_imports = {}  # Map file -> set of imported modules
        
    def analyze_file(self, file_path: str) -> None:
        """Analyze a single Python file and extract nodes and edges."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=file_path)
            visitor = CodeVisitor(file_path, self)
            visitor.visit(tree)
            
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def analyze_directory(self, directory_path: str) -> None:
        """Recursively analyze all Python files in a directory."""
        directory = Path(directory_path)
        python_files = list(directory.rglob("*.py"))
        
        for file_path in python_files:
            # Skip __pycache__ and virtual environments
            if '__pycache__' in str(file_path) or 'venv' in str(file_path):
                continue
            self.analyze_file(str(file_path))
    
    def add_node(self, node_type: str, name: str, file_path: str, line_number: int, 
                 metadata: Dict = None) -> None:
        """Add a node to the graph."""
        node = {
            'type': node_type,
            'name': name,
            'file_path': file_path,
            'line_number': line_number,
            'metadata': metadata or {}
        }
        self.nodes.append(node)
    
    def add_edge(self, source: str, target: str, relationship_type: str, 
                 file_path: str, line_number: int = None) -> None:
        """Add an edge to the graph."""
        edge = {
            'source': source,
            'target': target,
            'relationship_type': relationship_type,
            'file_path': file_path,
            'line_number': line_number
        }
        self.edges.append(edge)
    
    def get_nodes(self) -> List[Dict]:
        """Get all extracted nodes."""
        return self.nodes
    
    def get_edges(self) -> List[Dict]:
        """Get all extracted edges."""
        return self.edges


class CodeVisitor(ast.NodeVisitor):
    """AST visitor to extract code structure."""
    
    def __init__(self, file_path: str, analyzer: CodeAnalyzer):
        self.file_path = file_path
        self.analyzer = analyzer
        self.current_class = None
        self.current_function = None
        self.imports = {}  # Map alias -> module
        self.attribute_types = {}  # Map self.attr -> class name (e.g., self.db -> DatabaseConnection)
        
    def visit_Import(self, node):
        """Handle import statements."""
        for alias in node.names:
            module_name = alias.name
            alias_name = alias.asname if alias.asname else module_name.split('.')[-1]
            self.imports[alias_name] = module_name
            
            # Add import edge
            self.analyzer.add_edge(
                source=self.file_path,
                target=module_name,
                relationship_type='IMPORTS',
                file_path=self.file_path,
                line_number=node.lineno
            )
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Handle from ... import statements."""
        if node.module:
            for alias in node.names:
                imported_name = alias.name
                alias_name = alias.asname if alias.asname else imported_name
                full_import = f"{node.module}.{imported_name}"
                self.imports[alias_name] = full_import
                
                # Add import edge - try both full import and just the class/function name
                self.analyzer.add_edge(
                    source=self.file_path,
                    target=full_import,
                    relationship_type='IMPORTS',
                    file_path=self.file_path,
                    line_number=node.lineno
                )
                # Also try just the imported name (for cases where it's imported directly)
                self.analyzer.add_edge(
                    source=self.file_path,
                    target=imported_name,
                    relationship_type='IMPORTS',
                    file_path=self.file_path,
                    line_number=node.lineno
                )
        self.generic_visit(node)
    
    def visit_ClassDef(self, node):
        """Handle class definitions."""
        class_name = node.name
        full_name = f"{self.current_class}.{class_name}" if self.current_class else class_name
        
        # Add class node
        base_classes = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                base_classes.append(base.id)
            else:
                base_classes.append(str(base))
        
        self.analyzer.add_node(
            node_type='Class',
            name=full_name,
            file_path=self.file_path,
            line_number=node.lineno,
            metadata={'base_classes': base_classes}
        )
        
        # Add inheritance edges
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.analyzer.add_edge(
                    source=full_name,
                    target=base.id,
                    relationship_type='INHERITS',
                    file_path=self.file_path,
                    line_number=node.lineno
                )
        
        # Track current class
        previous_class = self.current_class
        self.current_class = full_name
        
        self.generic_visit(node)
        
        # Restore previous class context
        self.current_class = previous_class
    
    def visit_FunctionDef(self, node):
        """Handle function definitions."""
        func_name = node.name
        
        # Build full name with class context
        if self.current_class:
            full_name = f"{self.current_class}.{func_name}"
        elif self.current_function:
            full_name = f"{self.current_function}.{func_name}"
        else:
            full_name = func_name
        
        # Add function node
        node_type = 'Method' if self.current_class else 'Function'
        self.analyzer.add_node(
            node_type=node_type,
            name=full_name,
            file_path=self.file_path,
            line_number=node.lineno,
            metadata={'args': [arg.arg for arg in node.args.args]}
        )
        
        # Track parameter types for __init__ methods
        if func_name == '__init__' and self.current_class:
            # Extract parameter types from annotations
            for arg in node.args.args:
                if arg.arg != 'self' and arg.annotation:
                    # Try to extract type from annotation
                    if isinstance(arg.annotation, ast.Name):
                        param_type = arg.annotation.id
                        if param_type in self.imports:
                            imported_class = self.imports[param_type]
                            # Store parameter name -> class mapping
                            self.attribute_types[arg.arg] = imported_class.split('.')[-1]
        
        # Track current function
        previous_function = self.current_function
        self.current_function = full_name
        
        self.generic_visit(node)
        
        # Restore previous function context
        self.current_function = previous_function
    
    def visit_Assign(self, node):
        """Handle assignments to track self.attr = ClassInstance() patterns."""
        # Track assignments like: self.db = DatabaseConnection() or self.db = db_connection
        if len(node.targets) > 0 and isinstance(node.targets[0], ast.Attribute):
            attr = node.targets[0]
            if isinstance(attr.value, ast.Name) and attr.value.id == 'self':
                attr_name = attr.attr
                
                # Case 1: self.db = DatabaseConnection()
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        class_name = node.value.func.id
                        if class_name in self.imports:
                            imported_class = self.imports[class_name]
                            self.attribute_types[attr_name] = imported_class.split('.')[-1]
                
                # Case 2: self.db = db_connection (parameter assignment)
                elif isinstance(node.value, ast.Name):
                    param_name = node.value.id
                    # Use tracked parameter types from __init__ method
                    if param_name in self.attribute_types:
                        self.attribute_types[attr_name] = self.attribute_types[param_name]
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Handle function/method calls."""
        # Determine source
        source = self.current_function or self.current_class or self.file_path
        
        # Handle different call types
        if isinstance(node.func, ast.Name):
            # Direct function call: function_name()
            call_name = node.func.id
            # Check if it's an imported function/class
            if call_name in self.imports:
                target = self.imports[call_name]
            else:
                target = call_name
            
            # Add edge with the resolved target
            self.analyzer.add_edge(
                source=source,
                target=target,
                relationship_type='CALLS',
                file_path=self.file_path,
                line_number=node.lineno
            )
            
            # Also try just the call name (for direct function calls)
            if target != call_name:
                self.analyzer.add_edge(
                    source=source,
                    target=call_name,
                    relationship_type='CALLS',
                    file_path=self.file_path,
                    line_number=node.lineno
                )
        
        elif isinstance(node.func, ast.Attribute):
            # Method call: obj.method() or self.attribute.method()
            method_name = node.func.attr
            
            # Try to resolve the class for method calls like self.db.insert()
            if isinstance(node.func.value, ast.Attribute):
                # Handle self.something.method()
                if isinstance(node.func.value.value, ast.Name) and node.func.value.value.id == 'self':
                    attr_name = node.func.value.attr
                    # Try to resolve from tracked attribute types
                    if attr_name in self.attribute_types:
                        class_name = self.attribute_types[attr_name]
                        # Create edge with full qualified name
                        full_target = f"{class_name}.{method_name}"
                        self.analyzer.add_edge(
                            source=source,
                            target=full_target,
                            relationship_type='CALLS',
                            file_path=self.file_path,
                            line_number=node.lineno
                        )
            
            # Always add edge with just method name (for matching)
            self.analyzer.add_edge(
                source=source,
                target=method_name,
                relationship_type='CALLS',
                file_path=self.file_path,
                line_number=node.lineno
            )
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Handle attribute access (e.g., obj.method)."""
        # This is called for attribute access, which might be method calls
        self.generic_visit(node)
    
    def _get_call_name(self, node: ast.Call) -> str:
        """Extract the name of a function call."""
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            # Handle method calls like obj.method()
            # Return both the method name and try to resolve the object
            return node.func.attr
        elif isinstance(node.func, ast.Call):
            # Handle chained calls
            return None
        return None

