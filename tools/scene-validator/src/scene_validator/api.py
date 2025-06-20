"""API server for SceneValidator."""

import json
import logging
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from scene_validator.validator import SceneValidator
from scene_validator.schemas import ValidationResult

logger = logging.getLogger(__name__)


class ValidationRequest(BaseModel):
    """Request model for scene validation."""
    scene: Dict[str, Any]


def create_app(config: Dict[str, Any]) -> FastAPI:
    """Create and configure the FastAPI application.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        FastAPI: The configured application
    """
    app = FastAPI(
        title="SceneValidator API",
        description="API for validating scene composition and technical requirements",
        version="0.1.0"
    )
    
    # Initialize validator
    validator = SceneValidator(config)
    
    # Configure CORS if enabled
    if config.get("api_settings", {}).get("enable_cors", False):
        allowed_origins = config.get("api_settings", {}).get("allowed_origins", ["*"])
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    @app.post("/validate", response_model=ValidationResult)
    async def validate_scene(request: ValidationRequest):
        """Validate a scene from JSON payload."""
        try:
            result = validator.validate(request.scene)
            return result
        except Exception as e:
            logger.error(f"Error validating scene: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.post("/validate/upload", response_model=ValidationResult)
    async def validate_scene_upload(file: UploadFile = File(...)):
        """Validate a scene from uploaded file."""
        try:
            content = await file.read()
            scene_data = json.loads(content)
            result = validator.validate(scene_data)
            return result
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON file")
        except Exception as e:
            logger.error(f"Error validating scene: {e}")
            raise HTTPException(status_code=400, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "ok"}
    
    return app


def start_api_server(config: Dict[str, Any]):
    """Start the API server.
    
    Args:
        config: Configuration dictionary
    """
    api_settings = config.get("api_settings", {})
    host = api_settings.get("host", "0.0.0.0")
    port = api_settings.get("port", 8000)
    log_level = "debug" if api_settings.get("debug", False) else "info"
    
    app = create_app(config)
    
    logger.info(f"Starting API server at http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level=log_level)
