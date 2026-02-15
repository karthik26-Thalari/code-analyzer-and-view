# ui/graph_renderer.py
import streamlit as st
import streamlit.components.v1 as components
from pyvis.network import Network
import json
import networkx as nx
from pathlib import Path

class GraphRenderer:
    def __init__(self, height: int = 600):
        self.height = height
    
    def render_graph(self, graph, files_info: dict):
        """Render interactive graph"""
        
        if len(graph.nodes()) == 0:
            st.info("No nodes to display")
            return
        
        try:
            # Create network with BRIGHT THEME
            net = Network(
                height=f"{self.height}px",
                width="100%",
                directed=True,
                bgcolor="#ffffff",  # White background
                font_color="#333333",  # Dark text
                notebook=False
            )
            
            # Add nodes
            for node, node_data in graph.nodes(data=True):
                self._add_node(node, node_data, net, files_info)
            
            # Add edges
            for source, target, edge_data in graph.edges(data=True):
                self._add_edge(source, target, edge_data, net)
            
            # Configure options
            options = self._get_options()
            net.set_options(json.dumps(options))
            
            # Generate and display
            html = net.generate_html()
            components.html(html, height=self.height, scrolling=True)
            
        except Exception as e:
            st.error(f"Graph error: {str(e)}")
    
    def _add_node(self, node_id: str, node_data: dict, net: Network, files_info: dict):
        """Add node to network"""
        
        # Bright color scheme
        colors = {
            'folder': '#7ee787',  # Bright green
            'file': '#667eea',    # Bright blue
            'function': '#ff7b72', # Bright red
            'python': '#667eea',   # Blue
            'javascript': '#f1e05a', # Yellow
            'typescript': '#3178c6', # Blue
            'html': '#e34c26',    # Orange
            'css': '#563d7c',     # Purple
            'json': '#f0db4f',    # Yellow
            'default': '#6c757d'  # Gray
        }
        
        # Determine node type and color
        if 'folder::' in node_id:
            node_type = 'folder'
            color = colors['folder']
            label = f"📁 {node_id.replace('folder::', '')}"
            shape = 'box'
            size = 35
        elif '::ƒ::' in node_id:
            node_type = 'function'
            color = colors['function']
            func_name = node_id.split('::ƒ::')[-1]
            label = f"⚙️ {func_name}"
            shape = 'ellipse'
            size = 20
        else:
            node_type = 'file'
            file_info = files_info.get(node_id, {})
            file_ext = file_info.get('extension', '')
            
            # Color by file type
            if file_ext == '.py':
                color = colors['python']
            elif file_ext == '.js':
                color = colors['javascript']
            elif file_ext == '.ts':
                color = colors['typescript']
            elif file_ext == '.html':
                color = colors['html']
            elif file_ext == '.css':
                color = colors['css']
            elif file_ext == '.json':
                color = colors['json']
            else:
                color = colors['file']
            
            label = f"📄 {Path(node_id).name}"
            shape = 'box'
            size = 25
        
        # Add node
        net.add_node(
            node_id,
            label=label,
            title=node_data.get('title', label),
            color=color,
            shape=shape,
            size=size,
            borderWidth=2,
            borderWidthSelected=4
        )
    
    def _add_edge(self, source: str, target: str, edge_data: dict, net: Network):
        """Add edge to network"""
        
        # Bright edge colors
        colors = {
            'import': '#58a6ff',  # Bright blue
            'call': '#f778ba',    # Bright pink
            'contains': '#8b949e', # Gray
            'default': '#667eea'   # Blue
        }
        
        edge_type = edge_data.get('type', '')
        color = colors.get(edge_type, colors['default'])
        width = 2 if edge_type == 'import' else 1.5
        
        net.add_edge(
            source,
            target,
            color=color,
            width=width,
            arrows='to',
            smooth={'type': 'continuous'}
        )
    
    def _get_options(self):
        """Get graph options"""
        return {
            "physics": {
                "enabled": True,
                "stabilization": {
                    "enabled": True,
                    "iterations": 100
                },
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 100,
                    "springConstant": 0.08
                }
            },
            "interaction": {
                "hover": True,
                "tooltipDelay": 200,
                "hoverConnectedEdges": True,
                "dragNodes": True,
                "dragView": True,
                "zoomView": True
            },
            "edges": {
                "smooth": {
                    "type": "continuous"
                },
                "color": {
                    "inherit": "from"
                },
                "arrows": {
                    "to": {
                        "enabled": True,
                        "scaleFactor": 0.8
                    }
                }
            },
            "nodes": {
                "font": {
                    "size": 14,
                    "face": "Arial",
                    "color": "#333333"
                },
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "shadow": {
                    "enabled": True,
                    "color": "rgba(102, 126, 234, 0.2)",
                    "size": 10
                }
            }
        } 