# run.py
import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import streamlit
        import networkx
        import pyvis
        import openai
        import git
        import magic
        import sentence_transformers
        import dotenv
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        return False

def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def main():
    # Check if .env exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("Creating .env.example for you...")
        
        env_example = """# OpenRouter API Key (required)
OPENROUTER_API_KEY=sk-or-v1-your-api-key-here

# Optional OpenAI fallback
# OPENAI_API_KEY=sk-your-openai-key

# Model Settings
OPENROUTER_MODEL=meta-llama/llama-3.1-70b-instruct:free
EMBEDDING_MODEL=all-MiniLM-L6-v2
TEMPERATURE=0.3
MAX_TOKENS=1000

# File Handling
MAX_FILE_SIZE_MB=50"""
        
        with open(".env.example", "w") as f:
            f.write(env_example)
        
        print("📝 Created .env.example")
        print("📝 Please copy it to .env and add your OpenRouter API key")
        print("🔑 Get your key from: https://openrouter.ai/keys")
        return
    
    # Check dependencies
    if not check_dependencies():
        print("Installing missing dependencies...")
        install_dependencies()
    
    # Run the app
    print("🚀 Starting Intent-Aware Codebase Explorer...")
    print("🌐 Open http://localhost:8501 in your browser")
    
    os.system("streamlit run main_app.py")

if __name__ == "__main__":
    main()