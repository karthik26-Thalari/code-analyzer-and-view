# utils/git_utils.py
import git
import tempfile
from pathlib import Path
import streamlit as st

def clone_repository(url: str) -> Path:
    """Clone a git repository to a temporary directory"""
    temp_dir = tempfile.mkdtemp(prefix="repo_")
    
    try:
        st.info(f"Cloning {url}...")
        repo = git.Repo.clone_from(url, temp_dir, depth=1)
        st.success(f"Cloned {len(list(repo.iter_commits()))} commits")
        return Path(temp_dir)
    except Exception as e:
        raise Exception(f"Failed to clone repository: {str(e)}")