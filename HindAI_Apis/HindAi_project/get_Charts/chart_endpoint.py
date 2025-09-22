from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel
import os
from pathlib import Path

router = APIRouter()

class ImageRequest(BaseModel):
    file_path: str

@router.post("/get-image")
async def get_image(request: ImageRequest):
    """
    Endpoint to serve image files and HTML files by providing the file path
    """
    try:
        file_path = request.file_path
        
        # Normalize the path (handles both forward and backward slashes)
        normalized_path = os.path.normpath(file_path)
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if it's actually a file (not a directory)
        if not os.path.isfile(normalized_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Get file extension to determine media type
        file_extension = Path(normalized_path).suffix.lower()
        
        # If it's an HTML file, provide download option
        if file_extension in ['.html', '.htm']:
            return FileResponse(
                path=normalized_path,
                media_type='text/html',
                filename=file_name,
                headers={"Content-Disposition": f"attachment; filename={file_name}"}
            )
        
        media_type_map = {
            # Image types
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            # Other types
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.txt': 'text/plain'
        }
        
        media_type = media_type_map.get(file_extension, 'application/octet-stream')
        
        # Return the file
        return FileResponse(
            path=normalized_path,
            media_type=media_type,
            filename=os.path.basename(normalized_path)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

@router.get("/get-image/{file_name}")
async def get_image_by_name(file_name: str, base_path: str = "C:/Users/user/Desktop/newhostingfordynamic/agents/charts"):
    """
    Alternative endpoint to get files by filename from a base directory
    This endpoint serves images directly for display (not download)
    """
    try:
        # Construct full path
        full_path = os.path.join(base_path, file_name)
        normalized_path = os.path.normpath(full_path)
        
        # Security check - ensure the resolved path is within the base directory
        if not normalized_path.startswith(os.path.normpath(base_path)):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if file exists
        if not os.path.exists(normalized_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if it's actually a file
        if not os.path.isfile(normalized_path):
            raise HTTPException(status_code=400, detail="Path is not a file")
        
        # Get file extension for media type
        file_extension = Path(normalized_path).suffix.lower()
        
        # If it's an HTML file, return the content directly
        if file_extension in ['.html', '.htm']:
            with open(normalized_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            return HTMLResponse(content=html_content)
        
        media_type_map = {
            # Image types
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.svg': 'image/svg+xml',
            # Other types
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.txt': 'text/plain'
        }
        
        media_type = media_type_map.get(file_extension, 'application/octet-stream')
        
        # For images, serve inline (not as download)
        if file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg']:
            return FileResponse(
                path=normalized_path,
                media_type=media_type,
                headers={"Content-Disposition": "inline"}  # This prevents download
            )
        
        return FileResponse(
            path=normalized_path,
            media_type=media_type,
            filename=file_name
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error serving file: {str(e)}")

