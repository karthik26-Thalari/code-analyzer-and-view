# core/file_manager.py
import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional
import tempfile
from config.settings import Settings

class FileManager:
    def __init__(self):
        self.files: Dict[str, Dict] = {}
        self.file_tree: Dict = {}
        self.total_files = 0
        self.total_size = 0
        
    def scan_directory(self, directory: Path) -> Dict[str, Dict]:
        """Scan directory and collect file information"""
        self.files = {}
        self.file_tree = {}
        
        for root, dirs, files in os.walk(directory):
            # Remove ignored directories
            dirs[:] = [d for d in dirs if d not in Settings.IGNORE_DIRS]
            
            # Get relative path
            rel_root = Path(root).relative_to(directory)
            
            # Add directory to tree
            current = self.file_tree
            for part in rel_root.parts:
                current = current.setdefault(part, {})
            
            # Process files
            for file in files:
                if file in Settings.IGNORE_FILES:
                    continue
                    
                file_path = Path(root) / file
                rel_path = file_path.relative_to(directory)
                
                # Get file info
                file_info = self._get_file_info(file_path, rel_path)
                
                # Store in files dict
                self.files[str(rel_path)] = file_info
                
                # Add to tree
                if 'files' not in current:
                    current['files'] = []
                current['files'].append(file_info)
                
                self.total_files += 1
                self.total_size += file_info['size']
        
        return self.files
    
    def _get_file_info(self, file_path: Path, rel_path: Path) -> Dict:
        """Get detailed information about a file"""
        try:
            # Get file stats
            stat = file_path.stat()
            
            # Get file type
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # Read content (text files only)
            content = None
            if self._is_text_file(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                except:
                    try:
                        with open(file_path, 'r', encoding='latin-1') as f:
                            content = f.read()
                    except:
                        content = None
            
            # Get file info from settings
            file_info = Settings.get_file_info(str(rel_path))
            
            return {
                'path': str(rel_path),
                'name': file_path.name,
                'full_path': str(file_path),
                'size': stat.st_size,
                'size_human': self._human_readable_size(stat.st_size),
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'mime_type': mime_type or 'application/octet-stream',
                'content': content,
                'is_text': content is not None,
                'extension': file_path.suffix.lower(),
                'label': file_info['label'],
                'color': file_info['color'],
                'icon': file_info['icon'],
                'lines': len(content.splitlines()) if content else 0
            }
        except Exception as e:
            return {
                'path': str(rel_path),
                'name': file_path.name,
                'error': str(e),
                'size': 0,
                'label': 'Error',
                'color': '#FF0000',
                'icon': '❌'
            }
    
    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely text-based"""
        text_extensions = {ext for ext in Settings.FILE_EXTENSIONS.keys()}
        return file_path.suffix.lower() in text_extensions
    
    def _human_readable_size(self, size_bytes: int) -> str:
        """Convert bytes to human readable size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def get_file_by_path(self, path: str) -> Optional[Dict]:
        """Get file info by path"""
        return self.files.get(path)
    
    def search_files(self, query: str) -> List[Dict]:
        """Search files by name or content"""
        results = []
        query_lower = query.lower()
        
        for file_info in self.files.values():
            # Search in filename
            if query_lower in file_info['name'].lower():
                results.append(file_info)
                continue
            
            # Search in content (if text file)
            if file_info.get('content') and query_lower in file_info['content'].lower():
                results.append(file_info)
        
        return results
    
    def get_file_tree(self) -> Dict:
        """Get hierarchical file tree"""
        return self.file_tree