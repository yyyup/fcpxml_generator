#!/usr/bin/env python3
"""
FCPXML Generator for DaVinci Resolve
Entry point for the application
"""

import sys
import os

# Add the current directory to the Python path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.main_window import FCPXMLGeneratorApp

def main():
    """Main entry point for the application"""
    try:
        app = FCPXMLGeneratorApp()
        app.run()
    except Exception as e:
        import tkinter as tk
        from tkinter import messagebox
        
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Startup Error", f"Failed to start application:\n{str(e)}")
        print(f"Startup error: {e}")

if __name__ == "__main__":
    main()