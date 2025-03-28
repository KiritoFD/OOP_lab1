#!/usr/bin/env python
"""
Cleanup script to remove __pycache__ directories and .pyc files
which may cause import conflicts during testing.
"""
import os
import shutil
import sys

def cleanup_cache():
    """Remove __pycache__ directories and .pyc files"""
    root_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Remove __pycache__ directories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        if '__pycache__' in dirnames:
            cache_dir = os.path.join(dirpath, '__pycache__')
            print(f"Removing {cache_dir}")
            shutil.rmtree(cache_dir)
    
    # Remove .pyc files
    for dirpath, dirnames, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.pyc'):
                pyc_file = os.path.join(dirpath, filename)
                print(f"Removing {pyc_file}")
                os.remove(pyc_file)
    
    print("Cache cleanup complete")

if __name__ == "__main__":
    cleanup_cache()
    sys.exit(0)
