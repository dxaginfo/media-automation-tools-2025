"""Schema definitions for SceneValidator."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class Position(BaseModel):
    """Position in 3D space."""
    x: float
    y: float
    z: float


class Dimensions(BaseModel):
    """Dimensions in 3D space."""
    width: float
    height: float
    depth: float


class Resolution(BaseModel):
    """Screen or image resolution."""
    width: int
    height: int


class Element(BaseModel):
    """A scene element."""
    element_id: str
    element_type: str
    position: Position
    dimensions: Dimensions
    properties: Dict[str, Any] = Field(default_factory=dict)


class SceneData(BaseModel):
    """Input scene data schema."""
    scene_id: str
    project_id: str
    timestamp: datetime
    scene_type: str
    resolution: Resolution
    frame_rate: float
    color_space: str
    elements: List[Element]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ValidationError(BaseModel):
    """Error found during validation."""
    error_code: str
    error_message: str
    severity: str
    element_id: Optional[str] = None
    suggestion: Optional[str] = None


class ValidationWarning(BaseModel):
    """Warning found during validation."""
    warning_code: str
    warning_message: str
    element_id: Optional[str] = None
    suggestion: Optional[str] = None


class ValidationResult(BaseModel):
    """Result of scene validation."""
    scene_id: str
    validation_id: str
    timestamp: datetime
    valid: bool
    errors: List[ValidationError] = Field(default_factory=list)
    warnings: List[ValidationWarning] = Field(default_factory=list)
    performance_metrics: Dict[str, Any] = Field(default_factory=dict)
    validation_time_ms: int
