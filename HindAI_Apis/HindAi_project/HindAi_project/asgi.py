import os
import sys
from pathlib import Path

# Add the parent directory to Python path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(project_root))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HindAi_project.settings')

# Import Django and initialize it first
import django
django.setup()

from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from starlette.applications import Starlette
from fastapi.staticfiles import StaticFiles

# Import the FastAPI app
from main_api import app as fastapi_app

# Get Django ASGI application
django_asgi_app = get_asgi_application()

# Create an async handler for Django paths
async def django_app(scope, receive, send):
    if scope["type"] == "lifespan":
        return await fastapi_app(scope, receive, send)
    
    path = scope["path"]
    if path.startswith(("/admin", "/static/admin", "/django/admin")):
        if path.startswith("/django/"):
            scope["path"] = path.replace("/django", "", 1)
        return await django_asgi_app(scope, receive, send)
    
    return await fastapi_app(scope, receive, send)

# Add static files handling
fastapi_app.mount("/static", StaticFiles(directory="staticfiles"), name="static")

# Create the final application
application = django_app
