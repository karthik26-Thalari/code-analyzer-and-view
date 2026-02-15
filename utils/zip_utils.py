# utils/zip_utils.py
import zipfile
import tempfile
from pathlib import Path
import io

def extract_zip(zip_file) -> Path:
    """Extract ZIP file to temporary directory"""
    temp_dir = tempfile.mkdtemp(prefix="zip_")
    
    try:
        # Save uploaded file to bytes
        zip_bytes = io.BytesIO(zip_file.read())
        
        # Extract ZIP
        with zipfile.ZipFile(zip_bytes, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        return Path(temp_dir)
    except Exception as e:
        raise Exception(f"Failed to extract ZIP: {str(e)}")