# main_app.py - FIXED GRAPH CONTAINER AND AUTO-SHOW CODE
import streamlit as st
import os
import sys
from pathlib import Path
import tempfile
import mimetypes
import networkx as nx
import json
import streamlit.components.v1 as components
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Try imports with error handling
try:
    from config.settings import Settings
    from core.analyzer import CodeAnalyzer
    from core.graph_builder import GraphBuilder
    from core.explainer import OpenRouterExplainer
    from ui.graph_renderer import GraphRenderer
    from utils.git_utils import clone_repository
    from utils.zip_utils import extract_zip
    IMPORTS_OK = True
except ImportError as e:
    st.error(f"Import error: {e}")
    st.info("Please check that all required files exist in the correct directories.")
    IMPORTS_OK = False

# Initialize session state
if 'app' not in st.session_state:
    st.session_state.app = {
        'files': {},
        'graph': None,
        'selected_file': None,
        'selected_node': None,
        'analysis': {},
        'repo_name': None,
        'repo_loaded': False,
        'show_load': True,
        'search_query': '',
        'temp_dir': None,
        'active_tab': 'graph',
        'ai_prompt': '',
        'ai_response': '',
        'ai_history': [],
        'file_tree': {},
        'expanded_folders': set(),
        'ai_context': 'current_file',
        'node_click_trigger': None,
        'auto_show_code': False  # NEW: Flag to auto-show code
    }

# Page config - DARK THEME
st.set_page_config(
    page_title="🧠 Code Insight Pro",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# FIXED CSS - Better container and search styling
st.markdown("""
<style>
    /* IMPORT BETTER FONTS */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600&family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* DARK THEME BASE */
    .stApp {
        background: #0d1117;
        color: #c9d1d9;
        font-family: 'Inter', sans-serif;
        overflow-x: hidden;
    }
    
    /* FIX GRAPH CONTAINER - ABSOLUTE CONTAINMENT */
    .graph-wrapper {
        background: #000000;
        border-radius: 12px;
        border: 2px solid #30363d;
        padding: 5px;
        position: relative;
        height: 550px;
        overflow: hidden;
        width: 100%;
        box-sizing: border-box;
        margin: 0;
    }
    
    .graph-container {
        position: absolute;
        top: 5px;
        left: 5px;
        right: 5px;
        bottom: 5px;
        z-index: 1;
        border-radius: 8px;
        overflow: hidden !important;
        width: calc(100% - 10px) !important;
        height: calc(100% - 10px) !important;
    }
    
    /* Force PyVis to stay within container */
    .vis-network {
        width: 100% !important;
        height: 100% !important;
        overflow: hidden !important;
        position: absolute !important;
        top: 0 !important;
        left: 0 !important;
    }
    
    .vis-network canvas {
        width: 100% !important;
        height: 100% !important;
    }
    
    /* BETTER FONTS */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', sans-serif;
        font-weight: 600;
    }
    
    code, pre, .code-font {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
    }
    
    /* IMPROVED FILE EXPLORER - HIERARCHICAL */
    .file-explorer {
        background: #161b22;
        border-radius: 8px;
        padding: 10px;
        border: 1px solid #30363d;
        max-height: 70vh;
        overflow-y: auto;
    }
    
    .folder-item {
        padding: 6px 8px;
        margin: 2px 0;
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .folder-item:hover {
        background: #21262d;
    }
    
    .file-item {
        padding: 6px 8px 6px 24px;
        margin: 2px 0;
        cursor: pointer;
        border-radius: 4px;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
    }
    
    .file-item:hover {
        background: #21262d;
    }
    
    .file-item.selected {
        background: rgba(31, 111, 235, 0.2);
        border-left: 3px solid #1f6feb;
    }
    
    /* IMPROVED BUTTONS */
    .stButton > button {
        background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%);
        color: white;
        border: none;
        border-radius: 6px;
        padding: 8px 16px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(88, 166, 255, 0.3);
    }
    
    /* IMPROVED TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px;
        background: #161b22;
        padding: 6px;
        border-radius: 8px;
        margin-bottom: 16px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        color: #8b949e;
        border-radius: 6px;
        padding: 8px 16px;
        border: 1px solid transparent;
        font-family: 'Inter', sans-serif;
        font-size: 14px;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: #1f6feb !important;
        color: white !important;
        border-color: #58a6ff !important;
    }
    
    /* FIXED SEARCH RESULTS - NO HUGE SPACES */
    .search-result-item {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        transition: all 0.2s;
    }
    
    .search-result-item:hover {
        background: #21262d;
        border-color: #58a6ff;
    }
    
    .search-result-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 8px;
    }
    
    .search-result-content {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        background: #0d1117;
        padding: 10px;
        border-radius: 6px;
        overflow-x: auto;
        margin-top: 8px;
    }
    
    /* CODE EDITOR STYLING */
    .code-editor {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 0;
        overflow: hidden;
        width: 100%;
    }
    
    .code-header {
        background: #21262d;
        padding: 10px 15px;
        border-bottom: 1px solid #30363d;
        display: flex;
        align-items: center;
        gap: 10px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
    }
    
    .code-content {
        padding: 15px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        line-height: 1.5;
        max-height: 60vh;
        overflow-y: auto;
        width: 100%;
    }
    
    /* AUTO-SHOW CODE PANEL */
    .auto-code-panel {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 15px;
        margin-top: 15px;
        animation: slideIn 0.3s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* SCROLLBAR STYLING */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #161b22;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #30363d;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #58a6ff;
    }
    
    /* HIDE STREAMLIT BRANDING */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

class FixedGraphRenderer:
    def __init__(self, height: int = 500):
        self.height = height
    
    def render_graph(self, graph, files_info: dict, selected_node: str = None):
        """Render optimized graph with limited nodes"""
        
        if len(graph.nodes()) == 0:
            st.info("📊 No graph data available")
            return
        
        try:
            # LIMIT NODES FOR BETTER PERFORMANCE (max 80 nodes)
            all_nodes = list(graph.nodes(data=True))
            if len(all_nodes) > 80:
                st.warning(f"⚠️ Showing 80 of {len(all_nodes)} nodes for better performance")
                nodes_to_show = all_nodes[:80]
                # Create a subgraph with limited nodes
                limited_graph = graph.subgraph([n[0] for n in nodes_to_show])
            else:
                nodes_to_show = all_nodes
                limited_graph = graph
            
            from pyvis.network import Network
            
            # Create network with EXACT dimensions
            net = Network(
                height=f"{self.height}px",
                width="100%",
                directed=True,
                bgcolor="#000000",
                font_color="#ffffff",
                notebook=False,
                cdn_resources='remote'
            )
            
            # Set fixed dimensions in HTML
            net.width = "100%"
            net.height = f"{self.height}px"
            
            # Add limited nodes
            for node, node_data in nodes_to_show:
                self._add_node(node, node_data, net, files_info, selected_node)
            
            # Add edges only between shown nodes
            for source, target, edge_data in limited_graph.edges(data=True):
                self._add_edge(source, target, edge_data, net)
            
            # STRICT CONTAINER OPTIONS
            options = """
            {
              "width": "100%",
              "height": "100%",
              "physics": {
                "enabled": true,
                "stabilization": {
                  "enabled": true,
                  "iterations": 50
                },
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                  "gravitationalConstant": -30,
                  "centralGravity": 0.01,
                  "springLength": 80,
                  "springConstant": 0.05,
                  "damping": 0.5,
                  "avoidOverlap": 1
                }
              },
              "interaction": {
                "hover": true,
                "tooltipDelay": 100,
                "hideEdgesOnDrag": true,
                "hideNodesOnDrag": false
              },
              "nodes": {
                "font": {
                  "size": 12,
                  "face": "Arial",
                  "color": "#ffffff"
                },
                "borderWidth": 2,
                "borderWidthSelected": 4,
                "shadow": {
                  "enabled": true,
                  "color": "rgba(88, 166, 255, 0.3)",
                  "size": 10
                }
              },
              "edges": {
                "smooth": false,
                "color": {
                  "color": "#58a6ff",
                  "highlight": "#79c0ff"
                },
                "width": 1,
                "arrows": {
                  "to": {
                    "enabled": true,
                    "scaleFactor": 0.5
                  }
                }
              }
            }
            """
            
            net.set_options(options)
            
            # Generate HTML with STRICT container constraints
            html = net.generate_html()
            
            # Add STRICT JavaScript for container and clicks
            html = html.replace('</body>', '''
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Force strict container constraints
                const networkContainer = document.querySelector('.vis-network');
                const networkCanvas = document.querySelector('.vis-network canvas');
                
                if (networkContainer) {
                    networkContainer.style.width = '100%';
                    networkContainer.style.height = '100%';
                    networkContainer.style.overflow = 'hidden';
                    networkContainer.style.position = 'absolute';
                    networkContainer.style.top = '0';
                    networkContainer.style.left = '0';
                }
                
                if (networkCanvas) {
                    networkCanvas.style.width = '100%';
                    networkCanvas.style.height = '100%';
                }
                
                // Enhanced click handler with auto-redirect
                document.addEventListener('click', function(event) {
                    // Check if a node was clicked
                    let element = event.target;
                    while (element && !element.classList.contains('vis-node')) {
                        element = element.parentElement;
                    }
                    
                    if (element) {
                        // Get node ID from title
                        const nodeId = element.getAttribute('title');
                        if (nodeId) {
                            // Visual feedback - glowing effect
                            element.style.boxShadow = '0 0 20px rgba(88, 166, 255, 0.8)';
                            element.style.transition = 'box-shadow 0.3s ease';
                            
                            // Remove glow from other nodes
                            document.querySelectorAll('.vis-node').forEach(node => {
                                if (node !== element) {
                                    node.style.boxShadow = '';
                                }
                            });
                            
                            // Create URL with node parameter for auto-redirect
                            const currentUrl = new URL(window.location.href);
                            currentUrl.searchParams.set('clicked_node', nodeId);
                            currentUrl.searchParams.set('auto_show', 'true');
                            
                            // Redirect with the node parameter
                            window.location.href = currentUrl.toString();
                        }
                    }
                });
                
                // Force resize to container
                setTimeout(function() {
                    if (networkContainer && networkContainer.$network) {
                        networkContainer.$network.fit();
                        networkContainer.$network.redraw();
                    }
                }, 500);
            });
            
            // Handle window resize
            window.addEventListener('resize', function() {
                const networkContainer = document.querySelector('.vis-network');
                if (networkContainer) {
                    networkContainer.style.width = '100%';
                    networkContainer.style.height = '100%';
                    
                    if (networkContainer.$network) {
                        setTimeout(function() {
                            networkContainer.$network.fit();
                            networkContainer.$network.redraw();
                        }, 100);
                    }
                }
            });
            </script>
            </body>
            ''')
            
            # Display the graph in ABSOLUTE container
            st.markdown('<div class="graph-wrapper">', unsafe_allow_html=True)
            st.markdown('<div class="graph-container">', unsafe_allow_html=True)
            
            # Use components.html with exact dimensions
            components.html(html, height=self.height, scrolling=False)
            
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"Graph rendering error: {e}")
            import traceback
            st.code(traceback.format_exc())

    def _add_node(self, node_id: str, node_data: dict, net, files_info: dict, selected_node: str):
        """Add node with optimized styling"""
        
        # SIMPLIFIED NODE TYPES - NO FUNCTIONS
        if 'folder::' in node_id:
            color = '#7ee787'  # Green
            shape = 'box'
            label = Path(node_id.replace('folder::', '')).name
            size = 25
            icon = '📁'
        else:
            # File node
            file_info = files_info.get(node_id, {})
            ext = file_info.get('extension', '')
            
            # SIMPLIFIED COLOR MAPPING
            color_map = {
                '.py': '#1f6feb',   # Blue
                '.js': '#f1e05a',   # Yellow
                '.ts': '#3178c6',   # Blue
                '.html': '#e34c26', # Orange
                '.css': '#563d7c',  # Purple
                '.json': '#f0db4f', # Yellow
                '.md': '#083fa1',   # Blue
                '.txt': '#8b949e',  # Gray
                '.yaml': '#cb171e', # Red
                '.yml': '#cb171e',  # Red
            }
            
            color = color_map.get(ext, '#58a6ff')
            shape = 'box'
            label = Path(node_id).name[:12]  # Truncate long filenames
            size = 20
            
            # Add icon based on file type
            icon_map = {
                '.py': '🐍',
                '.js': '📜',
                '.ts': '📘',
                '.html': '🌐',
                '.css': '🎨',
                '.json': '📋',
                '.md': '📝',
                '.txt': '📄',
            }
            icon = icon_map.get(ext, '📄')
        
        # Check if selected
        is_selected = (selected_node == node_id)
        
        # Add node with label including icon
        net.add_node(
            node_id,
            label=f"{icon} {label}",
            title=node_id,
            color=color,
            shape=shape,
            size=size,
            borderWidth=3 if is_selected else 2,
            font={'size': 11, 'face': 'Arial', 'color': '#ffffff'}
        )
    
    def _add_edge(self, source: str, target: str, edge_data: dict, net):
        """Add simplified edge"""
        net.add_edge(source, target, color='#58a6ff', width=1, arrows='to')

def build_file_tree(files: dict):
    """Build hierarchical file tree from files dictionary"""
    tree = {}
    
    for file_path in files.keys():
        path = Path(file_path)
        parts = path.parts
        
        # Navigate through tree
        current = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                # It's a file
                if 'files' not in current:
                    current['files'] = []
                current['files'].append({
                    'name': part,
                    'path': file_path,
                    'info': files[file_path]
                })
            else:
                # It's a folder
                if part not in current:
                    current[part] = {}
                current = current[part]
    
    return tree

def render_file_tree(tree: dict, path: str = "", depth: int = 0):
    """Recursively render hierarchical file tree"""
    for key, value in tree.items():
        if key == 'files':
            # Render files in this folder
            for file_info in value:
                is_selected = st.session_state.app['selected_file'] == file_info['path']
                
                # File icon based on extension
                ext = file_info['info'].get('extension', '')
                icons = {
                    '.py': '🐍', '.js': '📜', '.ts': '📘',
                    '.jsx': '⚛️', '.tsx': '⚛️',
                    '.html': '🌐', '.css': '🎨',
                    '.json': '📋', '.yaml': '⚙️', '.yml': '⚙️',
                    '.md': '📝', '.txt': '📄',
                    '.sql': '🗄️', '.sh': '💻'
                }
                icon = icons.get(ext, '📄')
                
                # File item
                if st.button(
                    f"{icon} {file_info['name']}",
                    key=f"tree_file_{file_info['path']}",
                    use_container_width=True,
                    type="primary" if is_selected else "secondary"
                ):
                    st.session_state.app['selected_file'] = file_info['path']
                    st.rerun()
        else:
            # It's a folder
            folder_id = f"{path}/{key}" if path else key
            
            # Check if folder is expanded
            is_expanded = folder_id in st.session_state.app['expanded_folders']
            
            # Folder icon with rotation
            icon = "📁" if is_expanded else "📂"
            
            # Create expandable folder
            col1, col2 = st.columns([0.9, 0.1])
            with col1:
                if st.button(
                    f"{icon} {key}",
                    key=f"folder_{folder_id}",
                    use_container_width=True
                ):
                    if is_expanded:
                        st.session_state.app['expanded_folders'].remove(folder_id)
                    else:
                        st.session_state.app['expanded_folders'].add(folder_id)
                    st.rerun()
            
            # If expanded, render children
            if is_expanded:
                with st.container():
                    st.markdown('<div style="margin-left: 20px;">', unsafe_allow_html=True)
                    render_file_tree(value, folder_id, depth + 1)
                    st.markdown('</div>', unsafe_allow_html=True)

def main():
    """Main application"""
    
    if not IMPORTS_OK:
        st.error("❌ Some imports failed. Please check your files.")
        return
    
    if not Settings.OPENROUTER_API_KEY:
        st.error("❌ OpenRouter API key not found!")
        return
    
    # Check for node clicks via URL parameters
    clicked_node = None
    auto_show = False
    
    # Check for node click in URL
    if 'clicked_node' in st.query_params:
        clicked_node = st.query_params['clicked_node']
        auto_show = st.query_params.get('auto_show') == 'true'
    
    # Check for manual trigger
    elif st.session_state.app.get('node_click_trigger'):
        clicked_node = st.session_state.app['node_click_trigger']
        auto_show = True
        st.session_state.app['node_click_trigger'] = None
    
    # Handle the clicked node
    if clicked_node:
        st.session_state.app['selected_node'] = clicked_node
        
        # If it's a file node, select the file
        if clicked_node in st.session_state.app['files']:
            st.session_state.app['selected_file'] = clicked_node
            
            # Auto-show code if flag is set
            if auto_show:
                st.session_state.app['auto_show_code'] = True
                # Switch to file explorer tab to show the file
                st.session_state.app['active_tab'] = 'files'
        
        st.rerun()
    
    if st.session_state.app['show_load']:
        show_load_view()
    else:
        show_main_view()

def show_load_view():
    """Show load repository view"""
    
    st.markdown('<h1 style="color: #58a6ff; font-family: Inter;">🚀 Code Insight Pro</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color: #8b949e; font-family: Inter;">Visualize, Analyze, and Understand Your Codebase</p>', unsafe_allow_html=True)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📥 Load Repository")
        
        source = st.radio(
            "Select source:",
            ["GitHub URL", "Upload ZIP", "Local Directory"],
            label_visibility='collapsed'
        )
        
        if source == "GitHub URL":
            url = st.text_input("GitHub Repository URL:", placeholder="https://github.com/username/repository")
            if st.button("🚀 Clone & Analyze", use_container_width=True):
                if url:
                    load_github_repo(url)
                else:
                    st.warning("Please enter a GitHub URL")
        
        elif source == "Upload ZIP":
            zip_file = st.file_uploader("Choose ZIP file:", type=['zip'])
            if st.button("📦 Extract & Analyze", use_container_width=True):
                if zip_file:
                    load_zip_file(zip_file)
                else:
                    st.warning("Please upload a ZIP file")
        
        else:
            path = st.text_input("Local Directory Path:", placeholder="/path/to/your/project", value=".")
            if st.button("📂 Analyze Directory", use_container_width=True):
                if path:
                    load_local_path(path)
                else:
                    st.warning("Please enter a directory path")
    
    with col2:
        st.subheader("🚀 Quick Demos")
        
        demo_col1, demo_col2 = st.columns(2)
        with demo_col1:
            if st.button("🐍 Flask", use_container_width=True):
                load_github_repo("https://github.com/pallets/flask")
        with demo_col2:
            if st.button("⚡ FastAPI", use_container_width=True):
                load_github_repo("https://github.com/tiangolo/fastapi")
        
        st.divider()
        
        st.markdown("**Features:**")
        features = [
            "✅ **Fixed graph container** - No overflow issues",
            "✅ **Click nodes → Auto-show code** - Immediate file display",
            "✅ **Clean search results** - No huge spaces",
            "✅ **Hierarchical file explorer** - Easy navigation",
            "✅ **AI Assistant** - 3 context modes",
            "✅ **Syntax highlighting** - Professional code viewing"
        ]
        
        for feature in features:
            st.markdown(f"• {feature}")

def show_main_view():
    """Show main workspace"""
    
    # Header with better typography
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        st.markdown(f'<h2 style="color: #58a6ff; font-family: Inter;">📁 {st.session_state.app["repo_name"]}</h2>', unsafe_allow_html=True)
        
    with col2:
        file_count = len(st.session_state.app['files'])
        st.metric("Files", file_count)
    
    with col3:
        if st.session_state.app['graph']:
            node_count = len(st.session_state.app['graph'].nodes())
        else:
            node_count = 0
        st.metric("Nodes", node_count)
    
    with col4:
        if st.button("🔄 New", use_container_width=True):
            st.session_state.app['show_load'] = True
            st.rerun()
    
    st.divider()
    
    # Main tabs with better labels
    tabs = st.tabs(["📊 Graph View", "📁 File Explorer", "🤖 AI Assistant", "🔍 Search"])
    
    with tabs[0]:
        show_graph_view()
    
    with tabs[1]:
        show_file_explorer_view()
    
    with tabs[2]:
        show_ai_assistant()
    
    with tabs[3]:
        show_search_view()

def show_graph_view():
    """Show optimized graph view"""
    st.subheader("📊 Dependency Graph")
    
    if st.session_state.app['graph'] and st.session_state.app['files']:
        # Graph info
        node_count = len(st.session_state.app['graph'].nodes())
        edge_count = len(st.session_state.app['graph'].edges())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Nodes", node_count)
        with col2:
            st.metric("Connections", edge_count)
        with col3:
            if st.button("🔄 Refresh", use_container_width=True):
                st.session_state.app['selected_node'] = None
                st.rerun()
        
        # Manual node selection dropdown
        st.markdown("---")
        col1, col2 = st.columns([3, 1])
        with col1:
            # Create a dropdown of all file nodes
            file_nodes = [node for node in st.session_state.app['graph'].nodes() 
                         if 'folder::' not in node and node in st.session_state.app['files']]
            
            if file_nodes:
                selected_file = st.selectbox(
                    "Quick select file:",
                    file_nodes,
                    format_func=lambda x: Path(x).name,
                    index=0 if not st.session_state.app['selected_node'] else 
                    file_nodes.index(st.session_state.app['selected_node']) 
                    if st.session_state.app['selected_node'] in file_nodes else 0
                )
                
                if selected_file and selected_file != st.session_state.app['selected_node']:
                    st.session_state.app['selected_node'] = selected_file
                    st.session_state.app['selected_file'] = selected_file
                    st.session_state.app['auto_show_code'] = True
                    st.rerun()
        
        with col2:
            if st.session_state.app['selected_node']:
                if st.button("📄 View File", use_container_width=True):
                    st.session_state.app['auto_show_code'] = True
                    st.session_state.app['active_tab'] = 'files'
                    st.rerun()
        
        # Render the graph
        renderer = FixedGraphRenderer(height=500)
        renderer.render_graph(
            st.session_state.app['graph'],
            st.session_state.app['files'],
            st.session_state.app['selected_node']
        )
        
        # Show selected node info with auto-show
        if st.session_state.app['selected_node']:
            node_id = st.session_state.app['selected_node']
            if node_id in st.session_state.app['files']:
                file_info = st.session_state.app['files'][node_id]
                
                # Auto-show code panel
                if st.session_state.app.get('auto_show_code', False):
                    st.markdown('<div class="auto-code-panel">', unsafe_allow_html=True)
                    st.markdown(f"**📄 {file_info['name']}** (Auto-selected from graph)")
                    
                    # Show file preview
                    show_file_preview(file_info, limit_lines=20)
                    
                    # Button to view full file
                    if st.button("📖 Open Full File", key="open_full_from_graph", use_container_width=True):
                        st.session_state.app['auto_show_code'] = False
                        st.session_state.app['active_tab'] = 'files'
                        st.rerun()
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                else:
                    # Just show info without auto-display
                    with st.expander(f"📄 **{file_info['name']}** (Click to view)", expanded=False):
                        show_file_preview(file_info, limit_lines=15)
        
        # Legend
        st.markdown("---")
        st.markdown("**Legend:**")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown('📁 <span style="color: #7ee787">Folders</span>', unsafe_allow_html=True)
        with col2:
            st.markdown('📄 <span style="color: #1f6feb">Files</span>', unsafe_allow_html=True)
        with col3:
            st.markdown('🔗 <span style="color: #58a6ff">Connections</span>', unsafe_allow_html=True)
        
    else:
        st.info("No graph data available. Load a repository first.")

def show_file_explorer_view():
    """Show hierarchical file explorer"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("📂 File Explorer")
        
        if st.session_state.app['files']:
            # Build file tree if not already built
            if not st.session_state.app['file_tree']:
                st.session_state.app['file_tree'] = build_file_tree(st.session_state.app['files'])
            
            # Search
            search = st.text_input("🔍 Search files...", key="file_search")
            
            # File tree container
            st.markdown('<div class="file-explorer">', unsafe_allow_html=True)
            
            if search:
                # Show search results in compact format
                results = []
                for file_path, file_info in st.session_state.app['files'].items():
                    if search.lower() in file_info['name'].lower() or search.lower() in file_path.lower():
                        results.append(file_info)
                
                if results:
                    for file_info in results[:15]:  # Limit results
                        is_selected = st.session_state.app['selected_file'] == file_info['path']
                        
                        # Get icon
                        ext = file_info.get('extension', '')
                        icons = {
                            '.py': '🐍', '.js': '📜', '.ts': '📘',
                            '.html': '🌐', '.css': '🎨', '.json': '📋',
                            '.md': '📝', '.txt': '📄'
                        }
                        icon = icons.get(ext, '📄')
                        
                        if st.button(
                            f"{icon} {file_info['name']}",
                            key=f"search_{file_info['path']}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.app['selected_file'] = file_info['path']
                            st.rerun()
                else:
                    st.info("No files found")
            else:
                # Show hierarchical tree
                render_file_tree(st.session_state.app['file_tree'])
            
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No files loaded")
    
    with col2:
        show_file_content_view()

def show_file_content_view():
    """Show file content with better styling"""
    if st.session_state.app['selected_file']:
        file_path = st.session_state.app['selected_file']
        file_info = st.session_state.app['files'].get(file_path)
        
        if file_info:
            # File header with better styling
            st.markdown('<div class="code-editor">', unsafe_allow_html=True)
            
            # Header
            st.markdown(f'''
            <div class="code-header">
                <span style="color: #58a6ff; font-weight: 500;">{file_info.get('name', Path(file_path).name)}</span>
                <span style="color: #8b949e; margin-left: auto;">{file_path}</span>
            </div>
            ''', unsafe_allow_html=True)
            
            # File stats
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.caption(f"**Size:** {file_info.get('size_human', '0B')}")
            with col2:
                st.caption(f"**Lines:** {file_info.get('lines', 0)}")
            with col3:
                st.caption(f"**Type:** {Path(file_path).suffix or 'Unknown'}")
            with col4:
                if st.button("🤖 Analyze", key="analyze_file", use_container_width=True):
                    st.session_state.app['active_tab'] = 'ai'
                    st.session_state.app['ai_context'] = 'current_file'
                    st.session_state.app['ai_prompt'] = f"Explain this {Path(file_path).suffix} file"
                    st.rerun()
            
            # File content
            if file_info.get('content'):
                # Language mapping
                language_map = {
                    '.py': 'python',
                    '.js': 'javascript',
                    '.ts': 'typescript',
                    '.jsx': 'jsx',
                    '.tsx': 'tsx',
                    '.html': 'html',
                    '.css': 'css',
                    '.json': 'json',
                    '.yaml': 'yaml',
                    '.yml': 'yaml',
                    '.md': 'markdown',
                    '.sql': 'sql',
                    '.sh': 'bash'
                }
                
                language = language_map.get(file_info['extension'], 'text')
                
                st.markdown('<div class="code-content">', unsafe_allow_html=True)
                st.code(file_info['content'], language=language, line_numbers=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.warning("Cannot display file content (binary or unsupported)")
            
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Select a file from the explorer to view its content")

def show_file_preview(file_info: dict, limit_lines: int = 30):
    """Show a preview of a file"""
    if file_info.get('content'):
        # Show limited lines
        lines = file_info['content'].split('\n')[:limit_lines]
        preview = '\n'.join(lines)
        
        # Language for syntax highlighting
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json'
        }
        
        language = language_map.get(file_info.get('extension', ''), 'text')
        st.code(preview, language=language)
        
        # Calculate remaining lines properly
        total_lines = len(file_info['content'].split('\n'))
        if total_lines > limit_lines:
            remaining_lines = total_lines - limit_lines
            st.caption(f"... and {remaining_lines} more lines")
    else:
        st.info("No content to display")

def show_ai_assistant():
    """Show AI assistant with 3 context modes"""
    st.subheader("🤖 AI Code Assistant")
    
    # Context selection
    st.markdown("**📋 Select Context:**")
    
    ai_context = st.radio(
        "Context mode:",
        ["Current File", "Entire Project", "Custom Selection"],
        horizontal=True,
        key="ai_context_radio",
        label_visibility='collapsed'
    )
    
    # Map to internal values
    context_map = {
        "Current File": "current_file",
        "Entire Project": "entire_project", 
        "Custom Selection": "custom"
    }
    st.session_state.app['ai_context'] = context_map[ai_context]
    
    # Show context info
    if st.session_state.app['ai_context'] == 'current_file' and st.session_state.app['selected_file']:
        st.info(f"📄 **Context:** Current file: `{st.session_state.app['selected_file']}`")
    elif st.session_state.app['ai_context'] == 'entire_project':
        file_count = len(st.session_state.app['files'])
        st.info(f"📁 **Context:** Entire project ({file_count} files)")
    else:
        st.info("✏️ **Context:** Custom selection (enter below)")
    
    # Custom context input
    custom_context = ""
    if st.session_state.app['ai_context'] == 'custom':
        custom_context = st.text_area(
            "Enter custom context:",
            placeholder="Paste code or describe what you want to analyze...",
            height=150
        )
    
    # Action selection
    action = st.selectbox(
        "What would you like to do?",
        [
            "Explain code",
            "Refactor/Improve code", 
            "Find bugs/issues",
            "Add new feature",
            "Optimize performance",
            "Write documentation",
            "Generate tests",
            "Review code quality"
        ]
    )
    
    # Prompt input
    prompt = st.text_area(
        f"Your request ({action.lower()}):",
        placeholder=f"E.g., {action.lower()}...",
        height=100,
        key="ai_prompt_input"
    )
    
    # Generate button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("🚀 Generate", use_container_width=True, type="primary"):
            if prompt:
                generate_ai_response(action, prompt, custom_context)
            else:
                st.warning("Please enter a prompt")
    
    # Conversation history
    st.divider()
    st.subheader("💬 Conversation History")
    
    if st.session_state.app['ai_history']:
        for msg in st.session_state.app['ai_history'][-5:]:  # Show last 5 messages
            if msg['role'] == 'user':
                st.markdown(f'''
                <div style="padding: 12px 16px; margin: 8px 0; border-radius: 8px; background: rgba(31, 111, 235, 0.1); border-left: 4px solid #1f6feb;">
                    <strong>👤 You ({msg.get('context', 'Unknown')}):</strong><br>
                    {msg['content']}
                </div>
                ''', unsafe_allow_html=True)
            else:
                st.markdown(f'''
                <div style="padding: 12px 16px; margin: 8px 0; border-radius: 8px; background: rgba(121, 192, 255, 0.1); border-left: 4px solid #79c0ff;">
                    <strong>🤖 Assistant:</strong><br>
                    {msg['content']}
                </div>
                ''', unsafe_allow_html=True)
    else:
        st.info("💡 **Tip:** Select a context mode and ask the AI to analyze your code!")

def generate_ai_response(action: str, prompt: str, custom_context: str = ""):
    """Generate AI response with selected context"""
    try:
        explainer = OpenRouterExplainer()
        
        # Build context based on selection
        context_text = ""
        context_type = st.session_state.app['ai_context']
        
        if context_type == 'current_file' and st.session_state.app['selected_file']:
            file_info = st.session_state.app['files'].get(st.session_state.app['selected_file'])
            if file_info and file_info.get('content'):
                context_text = f"File: {st.session_state.app['selected_file']}\n\n{file_info['content'][:3000]}"
        
        elif context_type == 'entire_project':
            # Get overview of all files
            file_overview = []
            for file_path, file_info in list(st.session_state.app['files'].items())[:10]:  # Limit to 10 files
                if file_info.get('content'):
                    preview = file_info['content'][:200] + "..." if len(file_info['content']) > 200 else file_info['content']
                    file_overview.append(f"File: {file_path}\nPreview: {preview}\n")
            context_text = "Project Overview:\n" + "\n".join(file_overview)[:3000]
        
        elif context_type == 'custom' and custom_context:
            context_text = custom_context
        
        # Build full prompt
        full_prompt = f"""
        ACTION: {action}
        
        CONTEXT:
        {context_text}
        
        USER REQUEST: {prompt}
        
        Please provide a comprehensive response including:
        1. Analysis of the code/request
        2. Specific recommendations
        3. Code examples if applicable
        4. Best practices to follow
        5. Potential pitfalls to avoid
        """
        
        with st.spinner("🤖 AI is analyzing..."):
            response = explainer.explain_code(full_prompt, "", "")
            
            # Add to history
            st.session_state.app['ai_history'].append({
                'role': 'user',
                'content': f"{action}: {prompt}",
                'context': st.session_state.app['ai_context']
            })
            st.session_state.app['ai_history'].append({
                'role': 'assistant',
                'content': response
            })
            
            st.rerun()
            
    except Exception as e:
        st.error(f"AI error: {e}")

def show_search_view():
    """Show search view with FIXED formatting - no huge spaces"""
    st.subheader("🔍 Intent-Based Search")
    
    # Search input - compact
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Search for functionality:",
            placeholder="e.g., authentication, database connection, error handling...",
            value=st.session_state.app.get('search_query', ''),
            label_visibility="collapsed"
        )
    with col2:
        search_clicked = st.button("🔍 Search", use_container_width=True)
    
    # Handle search
    if search_clicked and query:
        st.session_state.app['search_query'] = query
        results = search_files(query)
        
        if results:
            st.success(f"Found {len(results)} results")
            
            # Display results in COMPACT format - no huge spaces
            for i, result in enumerate(results[:8]):  # Limit to 8 results
                # Use custom HTML for compact display
                st.markdown(f'''
                <div class="search-result-item">
                    <div class="search-result-header">
                        <span style="font-size: 18px;">{result['icon']}</span>
                        <span style="font-weight: 600; color: #58a6ff;">{result['name']}</span>
                        <span style="margin-left: auto; font-size: 12px; color: #8b949e;">Score: {result['score']}%</span>
                    </div>
                    <div style="font-size: 12px; color: #8b949e; margin-bottom: 5px;">
                        📍 {result['path']}
                    </div>
                </div>
                ''', unsafe_allow_html=True)
                
                # Show preview in expander
                with st.expander(f"Preview {i+1}", expanded=False):
                    if result.get('preview'):
                        st.code(result['preview'], language='python')
                    
                    # Action buttons in compact row
                    col_btn1, col_btn2, col_btn3 = st.columns(3)
                    with col_btn1:
                        if st.button(f"📄 Open", key=f"open_sr_{i}", use_container_width=True):
                            st.session_state.app['selected_file'] = result['path']
                            st.session_state.app['active_tab'] = 'files'
                            st.rerun()
                    with col_btn2:
                        if st.button(f"🤖 Explain", key=f"explain_sr_{i}", use_container_width=True):
                            st.session_state.app['selected_file'] = result['path']
                            st.session_state.app['active_tab'] = 'ai'
                            st.session_state.app['ai_context'] = 'current_file'
                            st.session_state.app['ai_prompt'] = f"Explain this code related to '{query}'"
                            st.rerun()
                    with col_btn3:
                        if st.button(f"📊 Show in Graph", key=f"graph_sr_{i}", use_container_width=True):
                            st.session_state.app['selected_node'] = result['path']
                            st.session_state.app['active_tab'] = 'graph'
                            st.session_state.app['auto_show_code'] = True
                            st.rerun()
        
        elif query:  # Only show warning if query was actually entered
            st.warning("No results found. Try different keywords.")
    
    # Show recent searches or help text
    elif not query:
        st.info("💡 **Search tips:**")
        tips = [
            "• Search by filename (e.g., 'main.py')",
            "• Search by functionality (e.g., 'authentication')",
            "• Search by file type (e.g., '.py' for Python files)",
            "• Results are ranked by relevance score"
        ]
        for tip in tips:
            st.markdown(tip)

def search_files(query: str):
    """Search files with relevance scoring"""
    results = []
    query_lower = query.lower()
    
    for file_path, file_info in st.session_state.app['files'].items():
        score = 0
        
        # Check filename (highest weight)
        if query_lower in file_info['name'].lower():
            score += 60
        
        # Check path
        if query_lower in file_path.lower():
            score += 30
        
        # Check content
        if file_info.get('content'):
            content_lower = file_info['content'].lower()
            if query_lower in content_lower:
                score += 20
                
                # Count occurrences
                occurrences = content_lower.count(query_lower)
                score += min(occurrences * 5, 20)
                
                # Get preview around first occurrence
                lines = file_info['content'].split('\n')
                preview = ""
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        start = max(0, i - 2)
                        end = min(len(lines), i + 3)
                        preview_lines = []
                        for j in range(start, end):
                            if j == i:
                                preview_lines.append(f"🔍 {lines[j]}")
                            else:
                                preview_lines.append(f"   {lines[j]}")
                        preview = '\n'.join(preview_lines)
                        break
                        
                if not preview and len(file_info['content']) > 0:
                    preview = file_info['content'][:200] + "..."
            else:
                preview = ""
        else:
            preview = ""
        
        if score > 0:
            # Get icon
            ext = file_info.get('extension', '')
            icons = {
                '.py': '🐍', '.js': '📜', '.ts': '📘',
                '.html': '🌐', '.css': '🎨', '.json': '📋',
                '.md': '📝', '.txt': '📄'
            }
            icon = icons.get(ext, '📄')
            
            results.append({
                'path': file_path,
                'name': file_info['name'],
                'icon': icon,
                'score': score,
                'preview': preview,
                'lines': file_info.get('lines', 0)
            })
    
    # Sort by score
    results.sort(key=lambda x: x['score'], reverse=True)
    return results

# Load functions
def load_github_repo(url: str):
    with st.spinner("🌐 Cloning repository..."):
        try:
            temp_dir = clone_repository(url)
            repo_name = url.split('/')[-1].replace('.git', '')
            analyze_repository(temp_dir, repo_name)
            st.session_state.app['show_load'] = False
            st.success(f"✅ Repository '{repo_name}' loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def load_zip_file(zip_file):
    with st.spinner("📦 Extracting files..."):
        try:
            temp_dir = extract_zip(zip_file)
            repo_name = zip_file.name.replace('.zip', '')
            analyze_repository(temp_dir, repo_name)
            st.session_state.app['show_load'] = False
            st.success(f"✅ Repository '{repo_name}' loaded successfully!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

def load_local_path(path: str):
    path_obj = Path(path)
    if path_obj.exists():
        with st.spinner("📂 Analyzing directory..."):
            try:
                analyze_repository(path_obj, path_obj.name)
                st.session_state.app['show_load'] = False
                st.success(f"✅ Repository '{path_obj.name}' loaded successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    else:
        st.error("❌ Directory does not exist")

def analyze_repository(directory: Path, repo_name: str):
    """Analyze repository and build graph"""
    state = st.session_state.app
    
    try:
        # Scan files
        files = {}
        for root, dirs, file_list in os.walk(directory):
            # Skip hidden and system directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'venv', '.git']]
            
            for file in file_list:
                if file.startswith('.'):
                    continue
                    
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(directory))
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    stat = file_path.stat()
                    ext = file_path.suffix.lower()
                    
                    files[rel_path] = {
                        'path': rel_path,
                        'name': file,
                        'content': content,
                        'size': stat.st_size,
                        'size_human': _human_size(stat.st_size),
                        'extension': ext,
                        'lines': len(content.splitlines())
                    }
                except:
                    files[rel_path] = {
                        'path': rel_path,
                        'name': file,
                        'content': None,
                        'size': 0,
                        'size_human': '0B',
                        'extension': file_path.suffix.lower(),
                        'lines': 0
                    }
        
        # Build hierarchical file tree
        state['file_tree'] = build_file_tree(files)
        
        # Build a simple graph (NO FUNCTION NODES)
        G = nx.DiGraph()
        
        # Add file nodes (limit to 50 for better performance)
        file_paths = list(files.keys())
        for file_path in file_paths[:50]:
            G.add_node(file_path, type='file', size=20)
        
        # Add folder nodes for top-level folders only
        top_folders = set()
        for file_path in file_paths[:30]:
            folder = str(Path(file_path).parent)
            if folder != '.' and folder not in top_folders and folder.count('/') < 2:
                top_folders.add(folder)
                folder_id = f"folder::{folder}"
                G.add_node(folder_id, type='folder', size=25)
                
                # Connect folder to its direct children files
                for f_path in file_paths[:20]:
                    if str(Path(f_path).parent) == folder:
                        G.add_edge(folder_id, f_path, type='contains')
        
        # Add simple connections between related files (same folder)
        for folder in list(top_folders)[:5]:
            folder_files = [f for f in file_paths if str(Path(f).parent) == folder][:5]
            for i, file1 in enumerate(folder_files):
                for j, file2 in enumerate(folder_files):
                    if i < j and file1.endswith('.py') and file2.endswith('.py'):
                        G.add_edge(file1, file2, type='import')
        
        state['files'] = files
        state['graph'] = G
        state['repo_name'] = repo_name
        state['selected_file'] = file_paths[0] if file_paths else None
        state['expanded_folders'] = set(['.'])  # Expand root by default
        state['auto_show_code'] = False
        
    except Exception as e:
        st.error(f"Analysis error: {e}")

def _human_size(size_bytes: int) -> str:
    """Convert bytes to human readable"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

if __name__ == "__main__":
    main()