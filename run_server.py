#!/usr/bin/env python
"""
ChemGist API Server Launcher
Simple script to start the API server
"""

import os
import sys
import subprocess

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🚀 ChemGist API Server Launcher")
    print("="*70)
    print("\n📋 What's happening:")
    print("  1. Starting Flask API server on http://localhost:5000")
    print("  2. Loading the fine-tuned chemistry model (first run may take 2-5 min)")
    print("  3. The frontend HTML will be served on the same port")
    print("\n⏳ First time setup:")
    print("  - The base model 'microsoft/Phi-3-mini-4k-instruct' will be downloaded")
    print("  - Subsequent runs will be much faster (uses cache)")
    print("  - Requires internet connection for first run only")
    print("\n🔗 Once running, open in your browser:")
    print("  http://localhost:5000")
    print("\n" + "="*70 + "\n")
    
    # Start the API server
    try:
        subprocess.run([sys.executable, "api.py"], cwd=os.path.dirname(__file__))
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)
