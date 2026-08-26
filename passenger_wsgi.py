import os
import sys

# Get the base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Import Django's WSGI application
from core.wsgi import application
