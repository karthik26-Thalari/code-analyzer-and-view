# core/graph_builder.py
import networkx as nx
from typing import Dict, List
from config.settings import Settings
from pathlib import Path  # ADD THIS IMPORT
import os

class GraphBuilder:
    def __init__(self):
        self.G = nx.DiGraph()
    
    def build_stacked_graph(self, files: Dict[str, Dict], analysis: Dict) -> nx.DiGraph:
        """Build graph with stacked folder visualization"""
        self.G.clear()
        
        # First pass: Add all file nodes
        for file_path, file_info in files.items():
            self.G.add_node(
                file_path,
                label=file_info['name'],
                color=file_info.get('color', Settings.THEME['node_file']),
                type='file',
                size=25
            )
        
        # Second pass: Organize into folders
        self._organize_folders(files)
        
        # Third pass: Add functions
        self._add_functions(analysis)
        
        # Fourth pass: Add relationships
        self._add_relationships(analysis)
        
        return self.G
    
    def _organize_folders(self, files: Dict):
        """Organize files into stacked folders"""
        folder_files = {}
        
        # Group files by their containing stacked folders
        for file_path in files.keys():
            path = Path(file_path)
            
            # Check each parent directory
            for parent in path.parents:
                parent_name = parent.name
                if parent_name in Settings.FOLDER_TYPES and Settings.FOLDER_TYPES[parent_name].get('stacked'):
                    if parent_name not in folder_files:
                        folder_files[parent_name] = []
                    folder_files[parent_name].append(file_path)
                    break
        
        # Create folder nodes
        for folder_name, folder_files_list in folder_files.items():
            folder_config = Settings.FOLDER_TYPES.get(folder_name, {})
            folder_id = f"folder::{folder_name}"
            
            self.G.add_node(
                folder_id,
                label=f"{folder_config.get('icon', '📁')} {folder_name}",
                color=folder_config.get('color', Settings.THEME['node_folder']),
                type='folder',
                size=35,
                contains=folder_files_list
            )
    
    def _add_functions(self, analysis: Dict):
        """Add function nodes"""
        for file_path, file_analysis in analysis.items():
            for func in file_analysis.get('functions', []):
                func_id = f"{file_path}::ƒ::{func['name']}"
                
                self.G.add_node(
                    func_id,
                    label=f"ƒ {func['name']}",
                    color=Settings.THEME['node_function'],
                    type='function',
                    size=20,
                    file=file_path,
                    line=func.get('line')
                )
    
    def _add_relationships(self, analysis: Dict):
        """Add import and call relationships"""
        # For now, add simple relationships
        # You can enhance this later
        
        # Add containment edges (folder -> file, file -> function)
        for node, node_data in self.G.nodes(data=True):
            if node_data.get('type') == 'folder':
                for file_path in node_data.get('contains', []):
                    if file_path in self.G:
                        self.G.add_edge(
                            node,
                            file_path,
                            type='contains',
                            color=Settings.THEME['edge_contain']
                        )
            
            elif node_data.get('type') == 'function':
                file_path = node_data.get('file')
                if file_path and file_path in self.G:
                    self.G.add_edge(
                        file_path,
                        node,
                        type='contains',
                        color=Settings.THEME['edge_contain']
                    )