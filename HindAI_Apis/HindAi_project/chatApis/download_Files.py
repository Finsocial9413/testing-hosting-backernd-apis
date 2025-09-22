from fastapi import FastAPI
import base64
from fastapi import APIRouter, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import os
from fastapi.responses import FileResponse
router = APIRouter()


@router.get("/download-md")
async def download_md(file_path: str):
    """
    Download a markdown (.md) file by absolute path.
    Query param: file_path=C:/path/to/file.md
    """
    try:
        # Normalize path (handles mixed slashes)
        normalized_path = os.path.normpath(file_path.strip().strip('"').strip("'"))
        if not normalized_path.lower().endswith(".md"):
            raise HTTPException(status_code=400, detail="Only .md files are allowed")
        if not os.path.isfile(normalized_path):
            raise HTTPException(status_code=404, detail="File not found")
        return FileResponse(
            path=normalized_path,
            media_type="text/markdown",
            filename=os.path.basename(normalized_path)
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")