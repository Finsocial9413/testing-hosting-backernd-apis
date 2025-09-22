import os
import sys
import django

# Add parent directories to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
hindai_apis_dir = os.path.dirname(current_dir)  # HindAI_Apis directory
project_root = os.path.dirname(hindai_apis_dir)  # project root directory

# Enable detailed logging
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("asgi")

# Add paths in the correct order
sys.path.insert(0, current_dir)      # For local module imports
sys.path.insert(0, hindai_apis_dir)  # For agno_adapter import
sys.path.insert(0, project_root)     # For HindAI module import

logger.info(f"Python path: {sys.path[:5]}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"Project directories: {current_dir}, {hindai_apis_dir}")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "HindAi_project.settings")
django.setup()

try:
    # Import the FastAPI app directly from the same directory
    from HindAi_project.main_api import app as fastapi_app
    logger.info("Successfully imported main_api app")
    
    # Create Django ASGI application
    from django.core.asgi import get_asgi_application
    django_application = get_asgi_application()
    logger.info("Successfully created Django ASGI application")

    # Import for FastAPI/Django integration
    from fastapi.middleware.wsgi import WSGIMiddleware

    # Mount Django application under /django path
    fastapi_app.mount("/django", WSGIMiddleware(django_application))
    logger.info("Successfully mounted Django application")

    # Export the FastAPI application as 'application' for ASGI servers
    application = fastapi_app
    
except Exception as e:
    logger.error(f"Error in ASGI setup: {e}", exc_info=True)
    # Re-raise so the server can show the error
    raise
