# ================================================================
# PythonAnywhere WSGI Configuration File
# ================================================================
# Paste the contents of this file into your PythonAnywhere
# WSGI configuration file.
#
# To find it:
#   Web tab → click the WSGI configuration file link
#   (looks like: /var/www/yourusername_pythonanywhere_com_wsgi.py)
#
# IMPORTANT: Replace "yourusername" with your actual PythonAnywhere username
# ================================================================

import sys
import os

# Add your project folder to the Python path
path = '/home/yourusername/sat_project'
if path not in sys.path:
    sys.path.insert(0, path)

# Import the Flask app
from app import app as application  # noqa
