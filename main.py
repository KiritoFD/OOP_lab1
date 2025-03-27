#!/usr/bin/env python

"""
HTML Editor - Main entry point
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from src.app.cli import CommandLineInterface

def main():
    """Main entry point for the HTML editor application"""
    print("HTML Editor - Starting...")
    cli = CommandLineInterface()
    cli.run()

if __name__ == "__main__":
    main()
