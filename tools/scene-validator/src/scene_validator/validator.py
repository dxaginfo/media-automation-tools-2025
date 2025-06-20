"""Core validator implementation for SceneValidator."""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

from scene_validator.schemas import (
    SceneData,
    ValidationError,
    ValidationWarning,
    ValidationResult
)
from scene_validator.gemini_validator import GeminiValidator
from scene_validator.cloud_storage import CloudStorageClient

logger = logging.getLogger(__name__)


class SceneValidator:
    """Main validator class for scene composition validation."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the validator with configuration.
        
        Args:
            config: Configuration dictionary or path to config file
        """
        if isinstance(config, str):
            with open(config, "r") as f:
                self.config = json.load(f)
        else:
            self.config = config
        
        # Initialize components based on configuration
        self._init_components()
        
        logger.info("SceneValidator initialized with configuration")
    
    def _init_components(self):
        """Initialize validator components based on configuration."""
        # Initialize Gemini validator if configured
        gemini_config = self.config.get("cloud_settings", {})
        if gemini_config.get("gemini_model"):
            try:
                self.gemini_validator = GeminiValidator(gemini_config)
                logger.info("Gemini validator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini validator: {e}")
                self.gemini_validator = None
        else:
            self.gemini_validator = None
        
        # Initialize cloud storage client if configured
        storage_config = self.config.get("cloud_settings", {})
        if storage_config.get("storage_bucket"):
            try:
                self.storage_client = CloudStorageClient(storage_config)
                logger.info("Cloud storage client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize cloud storage client: {e}")
                self.storage_client = None
        else:
            self.storage_client = None
    
    def validate_from_file(self, file_path: str) -> ValidationResult:
        """Validate a scene from a file.
        
        Args:
            file_path: Path to the scene file
            
        Returns:
            ValidationResult: The validation result
        """
        with open(file_path, "r") as f:
            scene_data = json.load(f)
        
        return self.validate(scene_data)
    
    def validate(self, scene_data: Dict[str, Any]) -> ValidationResult:
        """Validate a scene.
        
        Args:
            scene_data: Scene data dictionary
            
        Returns:
            ValidationResult: The validation result
        """
        start_time = time.time()
        
        # Parse scene data into Pydantic model
        try:
            scene = SceneData.model_validate(scene_data)
        except Exception as e:
            # If parsing fails, return validation result with error
            return ValidationResult(
                scene_id=scene_data.get("scene_id", "unknown"),
                validation_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                valid=False,
                errors=[
                    ValidationError(
                        error_code="INVALID_SCHEMA",
                        error_message=f"Failed to parse scene data: {str(e)}",
                        severity="critical",
                        suggestion="Ensure scene data conforms to the required schema"
                    )
                ],
                validation_time_ms=int((time.time() - start_time) * 1000)
            )
        
        # Perform validation
        errors, warnings = self._validate_scene(scene)
        
        # Create validation result
        result = ValidationResult(
            scene_id=scene.scene_id,
            validation_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            performance_metrics={
                "element_count": len(scene.elements),
                "complexity_score": self._calculate_complexity_score(scene)
            },
            validation_time_ms=int((time.time() - start_time) * 1000)
        )
        
        # Log validation result
        if result.valid:
            logger.info(f"Scene {scene.scene_id} validated successfully with {len(warnings)} warnings")
        else:
            logger.warning(f"Scene {scene.scene_id} validation failed with {len(errors)} errors")
        
        return result
    
    def _validate_scene(self, scene: SceneData) -> Tuple[List[ValidationError], List[ValidationWarning]]:
        """Perform validation on a scene.
        
        Args:
            scene: Scene data
            
        Returns:
            Tuple of (errors, warnings)
        """
        errors = []
        warnings = []
        
        # Basic validation checks
        self._validate_resolution(scene, errors, warnings)
        self._validate_color_space(scene, errors, warnings)
        self._validate_frame_rate(scene, errors, warnings)
        
        # Validate scene elements
        self._validate_elements(scene, errors, warnings)
        
        # If Gemini validator is available, use it for additional validation
        if self.gemini_validator:
            gemini_errors, gemini_warnings = self.gemini_validator.validate(scene)
            errors.extend(gemini_errors)
            warnings.extend(gemini_warnings)
        
        return errors, warnings
    
    def _validate_resolution(self, scene: SceneData, errors: List[ValidationError], warnings: List[ValidationWarning]):
        """Validate scene resolution."""
        min_resolution = self.config["validation_rules"].get("min_resolution", {})
        min_width = min_resolution.get("width", 0)
        min_height = min_resolution.get("height", 0)
        
        if scene.resolution.width < min_width or scene.resolution.height < min_height:
            errors.append(ValidationError(
                error_code="INVALID_RESOLUTION",
                error_message=f"Resolution {scene.resolution.width}x{scene.resolution.height} is below the minimum requirement of {min_width}x{min_height}",
                severity="high",
                suggestion=f"Increase resolution to at least {min_width}x{min_height}"
            ))
    
    def _validate_color_space(self, scene: SceneData, errors: List[ValidationError], warnings: List[ValidationWarning]):
        """Validate scene color space."""
        allowed_color_spaces = self.config["validation_rules"].get("allowed_color_spaces", [])
        
        if allowed_color_spaces and scene.color_space not in allowed_color_spaces:
            errors.append(ValidationError(
                error_code="INVALID_COLOR_SPACE",
                error_message=f"Color space '{scene.color_space}' is not in the allowed list: {', '.join(allowed_color_spaces)}",
                severity="medium",
                suggestion=f"Use one of the allowed color spaces: {', '.join(allowed_color_spaces)}"
            ))
    
    def _validate_frame_rate(self, scene: SceneData, errors: List[ValidationError], warnings: List[ValidationWarning]):
        """Validate scene frame rate."""
        # Example: warn about non-standard frame rates
        standard_rates = [23.976, 24, 25, 29.97, 30, 50, 59.94, 60]
        
        if scene.frame_rate not in standard_rates:
            warnings.append(ValidationWarning(
                warning_code="NON_STANDARD_FRAME_RATE",
                warning_message=f"Frame rate {scene.frame_rate} is not a standard frame rate",
                suggestion=f"Consider using a standard frame rate: {', '.join(map(str, standard_rates))}"
            ))
    
    def _validate_elements(self, scene: SceneData, errors: List[ValidationError], warnings: List[ValidationWarning]):
        """Validate scene elements."""
        element_rules = self.config["validation_rules"].get("element_rules", {})
        allow_unknown = self.config["validation_rules"].get("allow_unknown_elements", True)
        
        for element in scene.elements:
            # Check if element type is allowed
            if not allow_unknown and element.element_type not in element_rules:
                errors.append(ValidationError(
                    error_code="UNKNOWN_ELEMENT_TYPE",
                    error_message=f"Element type '{element.element_type}' is not allowed",
                    severity="medium",
                    element_id=element.element_id,
                    suggestion=f"Use one of the allowed element types: {', '.join(element_rules.keys())}"
                ))
                continue
            
            # Skip validation for unknown element types if they are allowed
            if element.element_type not in element_rules:
                continue
            
            # Validate required properties
            rules = element_rules[element.element_type]
            required_properties = rules.get("required_properties", [])
            for prop in required_properties:
                if prop not in element.properties:
                    errors.append(ValidationError(
                        error_code="MISSING_REQUIRED_PROPERTY",
                        error_message=f"Element '{element.element_id}' is missing required property '{prop}'",
                        severity="high",
                        element_id=element.element_id,
                        suggestion=f"Add the '{prop}' property to the element"
                    ))
            
            # Validate property constraints
            constraints = rules.get("constraints", {})
            for constraint_name, constraint_value in constraints.items():
                if constraint_name.endswith("_range"):
                    # Handle range constraints
                    prop_name = constraint_name.replace("_range", "")
                    if prop_name in element.properties:
                        prop_value = element.properties[prop_name]
                        min_val, max_val = constraint_value
                        if prop_value < min_val or prop_value > max_val:
                            errors.append(ValidationError(
                                error_code="PROPERTY_OUT_OF_RANGE",
                                error_message=f"Property '{prop_name}' value {prop_value} is outside the allowed range [{min_val}, {max_val}]",
                                severity="medium",
                                element_id=element.element_id,
                                suggestion=f"Adjust '{prop_name}' to be within range [{min_val}, {max_val}]"
                            ))
    
    def _calculate_complexity_score(self, scene: SceneData) -> float:
        """Calculate a complexity score for the scene.
        
        This is a simple example - in a real implementation, this would be more sophisticated.
        """
        # Basic formula: element count * (resolution factor) * (frame rate factor)
        element_count = len(scene.elements)
        resolution_factor = (scene.resolution.width * scene.resolution.height) / (1920 * 1080)  # Normalized to HD
        frame_rate_factor = scene.frame_rate / 24.0  # Normalized to 24fps
        
        return element_count * resolution_factor * frame_rate_factor
