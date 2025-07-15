"""
Minimal dotenv implementation for AURACLE bot
Fallback when python-dotenv is not available
"""
import os

def load_dotenv(path=None):
    """Load environment variables from .env file"""
    if path is None:
        path = ".env"
    
    if not os.path.exists(path):
        return
    
    try:
        with open(path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        os.environ[key] = value
    except Exception as e:
        print(f"Warning: Could not load .env file: {e}")