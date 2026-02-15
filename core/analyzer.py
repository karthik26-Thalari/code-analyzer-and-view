import ast
import os
from typing import Dict, List, Set, Tuple
import re

class CodeAnalyzer:
    def __init__(self):
        self.functions: List[Dict] = []
        self.imports_map: Dict[str, List[str]] = {}  # file -> imported files
        self.function_calls: Dict[str, List[str]] = {}  # function -> called functions
        
    def analyze_repository(self, directory: str) -> Dict[str, Dict]:
        """Analyze all Python files in repository"""
        results = {}
        
        for root, dirs, files in os.walk(directory):
            # Skip common directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'node_modules']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, directory)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    analysis = self.analyze_python_file(rel_path, content)
                    results[rel_path] = analysis
        
        return results
    
    def analyze_python_file(self, file_path: str, content: str) -> Dict:
        """Analyze Python file and extract imports and function calls"""
        file_info = {
            'functions': [],
            'imports': [],
            'function_calls': [],
            'imported_files': set(),
            'content': content
        }
        
        try:
            tree = ast.parse(content)
            
            # Extract imports
            imports = self._extract_imports(tree, file_path)
            file_info['imports'] = imports
            file_info['imported_files'] = {imp['module'] for imp in imports if '.' in imp['module']}
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = self._extract_function_info(node, content, file_path)
                    file_info['functions'].append(func_info)
                    self.functions.append(func_info)
                    
                    # Extract calls from this function
                    calls = self._extract_calls_from_function(node, content)
                    func_info['calls'] = calls
                    self.function_calls[func_info['name']] = calls
            
        except SyntaxError as e:
            file_info['error'] = f"Syntax error: {e}"
        
        return file_info
    
    def _extract_imports(self, tree: ast.AST, file_path: str) -> List[Dict]:
        """Extract all imports from file"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'module': alias.name,
                        'alias': alias.asname,
                        'type': 'import',
                        'line': node.lineno
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    full_module = f"{module}.{alias.name}" if module else alias.name
                    imports.append({
                        'module': full_module,
                        'alias': alias.asname,
                        'type': 'from_import',
                        'line': node.lineno,
                        'level': node.level
                    })
        
        return imports
    
    def _extract_function_info(self, node: ast.FunctionDef, content: str, file_path: str) -> Dict:
        """Extract information from function definition"""
        # Get arguments
        args = []
        if node.args.args:
            for arg in node.args.args:
                args.append(arg.arg)
        
        # Get function code
        func_code = ast.get_source_segment(content, node)
        
        return {
            'name': node.name,
            'file': file_path,
            'line': node.lineno,
            'args': args,
            'docstring': ast.get_docstring(node),
            'code': func_code,
            'full_code': content.split('\n')[node.lineno-1:node.end_lineno] if hasattr(node, 'end_lineno') else [],
            'calls': []
        }
    
    def _extract_calls_from_function(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract function calls from a function"""
        calls = []
        
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    calls.append(child.func.id)
                elif isinstance(child.func, ast.Attribute):
                    # Handle method calls like obj.method()
                    calls.append(child.func.attr)
        
        return calls
    
    def find_function_by_name(self, function_name: str) -> List[Dict]:
        """Find functions by name"""
        return [func for func in self.functions if function_name.lower() in func['name'].lower()]
    
    def search_in_code(self, search_text: str) -> List[Dict]:
        """Search for text in all functions"""
        results = []
        search_lower = search_text.lower()
        
        for func in self.functions:
            # Search in function name
            if search_lower in func['name'].lower():
                results.append({
                    'type': 'function_name',
                    'function': func,
                    'match': f"Function name: {func['name']}",
                    'score': 1.0
                })
            
            # Search in function code
            if func.get('code') and search_lower in func['code'].lower():
                results.append({
                    'type': 'function_code',
                    'function': func,
                    'match': f"Code contains: {search_text}",
                    'score': 0.8
                })
            
            # Search in docstring
            if func.get('docstring') and search_lower in func['docstring'].lower():
                results.append({
                    'type': 'docstring',
                    'function': func,
                    'match': f"Docstring contains: {search_text}",
                    'score': 0.9
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)