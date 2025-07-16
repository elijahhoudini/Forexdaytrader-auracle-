
"""
Minimal dotenv implementation
============================

Simple .env file loader when python-dotenv is not available.
"""

import os

def load_dotenv(dotenv_path='.env'):
    """
    Load environment variables from .env file.
    
    Args:
        dotenv_path (str): Path to .env file
    """
    if not os.path.exists(dotenv_path):
        return
    
    try:
        with open(dotenv_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    os.environ[key] = value
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")
