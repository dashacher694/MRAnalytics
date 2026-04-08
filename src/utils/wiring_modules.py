"""
Utility for finding wiring modules for dependency injection
"""
import os
from typing import List


def find_wiring_modules() -> List[str]:
    """
    Find all modules that need to be wired for dependency injection.
    
    Returns:
        List of module paths that contain API endpoints or other components
        that need dependency injection.
    """
    wiring_modules = []
    
    # Base path for modules
    base_path = "src.modules"
    modules_dir = os.path.join("src", "modules")
    
    if not os.path.exists(modules_dir):
        return wiring_modules
    
    # Walk through all modules and find API files
    for root, dirs, files in os.walk(modules_dir):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        
        for file in files:
            if file == "api.py":
                # Convert file path to module path
                rel_path = os.path.relpath(root, ".")
                module_path = rel_path.replace(os.sep, ".")
                api_module = f"{module_path}.api"
                wiring_modules.append(api_module)
    
    return wiring_modules
