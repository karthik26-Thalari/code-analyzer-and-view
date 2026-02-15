import streamlit as st
from pathlib import Path
from typing import Dict, List

class FileExplorer:
    def __init__(self):
        pass
    
    def display_file_tree(self, file_tree: Dict, selected_file: str = None):
        """Display hierarchical file tree"""
        st.subheader("📁 File Explorer")
        
        with st.container():
            self._render_tree_node(file_tree, selected_file)
    
    def _render_tree_node(self, node: Dict, selected_file: str, path: str = "", level: int = 0):
        """Recursively render tree node"""
        for key, value in node.items():
            if key == 'files':
                for file_info in value:
                    is_selected = selected_file == file_info['path']
                    
                    # Create display text with icon
                    display_text = f"{file_info.get('icon', '📄')} {file_info['name']}"
                    
                    # Add badge for file type
                    badge = f"`{file_info.get('label', 'FILE')}`"
                    
                    col1, col2 = st.columns([6, 1])
                    with col1:
                        if st.button(
                            f"{' ' * (level * 4)}{display_text}",
                            key=f"file_{file_info['path']}",
                            use_container_width=True,
                            type="primary" if is_selected else "secondary"
                        ):
                            st.session_state.selected_file = file_info['path']
                            st.rerun()
                    with col2:
                        st.caption(badge)
            else:
                # It's a directory
                with st.expander(f"📁 {key}", expanded=level < 2):
                    new_path = f"{path}/{key}" if path else key
                    self._render_tree_node(value, selected_file, new_path, level + 1)
    
    def display_file_content(self, file_info: Dict):
        """Display file content with syntax highlighting"""
        
        st.subheader(f"{file_info.get('icon', '📄')} {file_info['name']}")
        
        # File metadata
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Size", file_info.get('size_human', 'N/A'))
        with col2:
            st.metric("Lines", file_info.get('lines', 'N/A'))
        with col3:
            st.metric("Type", file_info.get('label', 'Unknown'))
        with col4:
            st.metric("Path", file_info['path'])
        
        st.divider()
        
        # File content
        if file_info.get('content'):
            # Determine language for syntax highlighting
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
                '.sh': 'bash',
                '.bash': 'bash'
            }
            
            language = language_map.get(file_info['extension'], 'text')
            
            st.code(file_info['content'], language=language, line_numbers=True)
        else:
            st.warning("Binary file or cannot read content")
    
    def display_file_stats(self, files: Dict[str, Dict]):
        """Display file statistics"""
        if not files:
            return
        
        total_size = sum(f.get('size', 0) for f in files.values())
        total_lines = sum(f.get('lines', 0) for f in files.values())
        
        # Count by type
        type_counts = {}
        for file_info in files.values():
            file_type = file_info.get('label', 'Unknown')
            type_counts[file_type] = type_counts.get(file_type, 0) + 1
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Total Files", len(files))
        with col2:
            st.metric("📊 Total Size", self._human_readable_size(total_size))
        with col3:
            st.metric("📝 Total Lines", f"{total_lines:,}")
        
        # File type distribution
        st.subheader("📈 File Type Distribution")
        for file_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            st.progress(count / len(files), text=f"{file_type}: {count} files")
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"