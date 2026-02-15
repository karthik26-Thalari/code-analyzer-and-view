# config/settings.py
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "xiaomi/mimo-v2-flash:free")
    
    # Model Settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    TEMPERATURE = float(os.getenv("TEMPERATURE", 0.3))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", 2000))
    
    # App Theme - DARK THEME
    THEME = {
        'bg_primary': '#0d1117',
        'bg_secondary': '#161b22',
        'bg_tertiary': '#21262d',
        'text_primary': '#c9d1d9',
        'text_secondary': '#8b949e',
        'border': '#30363d',
        'accent': '#58a6ff',
        'accent_hover': '#1f6feb',
        'success': '#238636',
        'warning': '#9e6a03',
        'error': '#f85149',
        'node_file': '#1f6feb',
        'node_folder': '#7ee787',
        'node_function': '#ff7b72',
        'edge_import': '#58a6ff',
        'edge_call': '#f778ba',
        'edge_contain': '#8b949e',
    }
    
    # File extensions with DARK THEME colors
    FILE_EXTENSIONS = {
        # Python files
        '.py': {'label': 'Python', 'color': '#1f6feb', 'icon': '🐍', 'type': 'code'},
        # Config files
        '.json': {'label': 'JSON', 'color': '#f0883e', 'icon': '📋', 'type': 'config'},
        '.yaml': {'label': 'YAML', 'color': '#f0883e', 'icon': '⚙️', 'type': 'config'},
        '.yml': {'label': 'YAML', 'color': '#f0883e', 'icon': '⚙️', 'type': 'config'},
        # Web files
        '.html': {'label': 'HTML', 'color': '#e34c26', 'icon': '🌐', 'type': 'web'},
        '.css': {'label': 'CSS', 'color': '#563d7C', 'icon': '🎨', 'type': 'web'},
        '.js': {'label': 'JavaScript', 'color': '#f1e05a', 'icon': '📜', 'type': 'code'},
        '.ts': {'label': 'TypeScript', 'color': '#2b7489', 'icon': '📘', 'type': 'code'},
        '.jsx': {'label': 'React JSX', 'color': '#61dafb', 'icon': '⚛️', 'type': 'code'},
        '.tsx': {'label': 'React TSX', 'color': '#2b7489', 'icon': '⚛️', 'type': 'code'},
        # Documentation
        '.md': {'label': 'Markdown', 'color': '#083fa1', 'icon': '📝', 'type': 'docs'},
        '.txt': {'label': 'Text', 'color': '#8b949e', 'icon': '📄', 'type': 'docs'},
        # Other
        '.sql': {'label': 'SQL', 'color': '#e38c00', 'icon': '🗄️', 'type': 'data'},
    }
    
    # Folder types
    FOLDER_TYPES = {
        'node_modules': {'color': '#8957e5', 'icon': '📦', 'stacked': True},
        'venv': {'color': '#7ee787', 'icon': '🐍', 'stacked': True},
        '.git': {'color': '#8b949e', 'icon': '📁', 'stacked': True},
        '__pycache__': {'color': '#8b949e', 'icon': '⚡', 'stacked': True},
        'dist': {'color': '#f0883e', 'icon': '📦', 'stacked': True},
        'build': {'color': '#f0883e', 'icon': '🔨', 'stacked': True},
    }
    
    # Ignored directories
    IGNORE_DIRS = {
        '__pycache__', '.git', '.github', '.vscode', '.idea',
        'node_modules', 'vendor', 'venv', 'env',
        'dist', 'build', 'target', 'out', 'bin', 'obj',
    }
    
    @classmethod
    def get_file_color(cls, file_path: str) -> str:
        """Get color based on file type"""
        import os
        from pathlib import Path
        
        path = Path(file_path)
        ext = path.suffix.lower()
        
        if ext in cls.FILE_EXTENSIONS:
            return cls.FILE_EXTENSIONS[ext]['color']
        
        # Default colors
        if 'test' in file_path.lower():
            return cls.THEME['warning']
        elif 'config' in file_path.lower() or 'settings' in file_path.lower():
            return cls.THEME['accent']
        elif 'util' in file_path.lower():
            return cls.THEME['success']
        
        return cls.THEME['node_file']
    
    @classmethod
    def validate_settings(cls):
        """Validate required settings - FIXED METHOD NAME"""
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY is required in .env file")
        return True