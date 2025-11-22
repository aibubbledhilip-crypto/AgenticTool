#!/usr/bin/env python3
"""
DVSum Agentic AI Automation Tool
Run this script to start the web application.
"""

import os
import sys

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from main import app

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    print(f"""
    ╔══════════════════════════════════════════════════════════════╗
    ║         DVSum Agentic AI Automation Tool                    ║
    ╠══════════════════════════════════════════════════════════════╣
    ║  Server starting on: http://{host}:{port}
    ║  Debug mode: {debug}
    ║                                                              ║
    ║  Open your browser and navigate to the URL above            ║
    ║  to access the GUI interface.                               ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    app.run(host=host, port=port, debug=debug)
