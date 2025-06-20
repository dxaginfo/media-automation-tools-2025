#!/usr/bin/env python3
"""
SceneValidator main module - entry point for CLI, API, and library usage.
"""

import json
import logging
import os
import sys
import time
from typing import Any, Dict, List, Optional, Union
import uuid

import typer
from pydantic import BaseModel, Field

from scene_validator.validator import SceneValidator
from scene_validator.schemas import ValidationResult
from scene_validator.api import start_api_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("scene_validator")

app = typer.Typer(help="SceneValidator: Validate scene composition and technical requirements")


@app.command()
def validate(
    scene: str = typer.Option(..., help="Path to scene file or JSON string"),
    config: str = typer.Option("config.json", help="Path to config file"),
    output: Optional[str] = typer.Option(None, help="Path to output file (default: stdout)"),
    format: str = typer.Option("json", help="Output format: json, text, or yaml"),
    verbose: bool = typer.Option(False, help="Enable verbose output"),
):
    """Validate a scene file against the configuration rules."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    try:
        with open(config, "r") as f:
            config_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Initialize validator
    validator = SceneValidator(config_data)
    
    # Determine if input is a file path or JSON string
    if os.path.isfile(scene):
        try:
            result = validator.validate_from_file(scene)
        except Exception as e:
            logger.error(f"Error validating scene file: {e}")
            sys.exit(1)
    else:
        try:
            # Assume it's a JSON string
            scene_data = json.loads(scene)
            result = validator.validate(scene_data)
        except json.JSONDecodeError:
            logger.error("Invalid JSON string provided")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error validating scene data: {e}")
            sys.exit(1)
    
    # Process output
    if format == "json":
        output_data = result.model_dump_json(indent=2)
    elif format == "yaml":
        import yaml
        output_data = yaml.dump(result.model_dump())
    elif format == "text":
        output_data = format_text_output(result)
    else:
        logger.error(f"Unsupported output format: {format}")
        sys.exit(1)
    
    if output:
        with open(output, "w") as f:
            f.write(output_data)
    else:
        print(output_data)
    
    # Exit with appropriate status code
    sys.exit(0 if result.valid else 1)


@app.command()
def serve(
    config: str = typer.Option("config.json", help="Path to config file"),
    host: Optional[str] = typer.Option(None, help="Host to bind API server"),
    port: Optional[int] = typer.Option(None, help="Port for API server"),
):
    """Start the API server for scene validation."""
    # Load configuration
    try:
        with open(config, "r") as f:
            config_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Override config with command line arguments if provided
    if host:
        config_data["api_settings"]["host"] = host
    if port:
        config_data["api_settings"]["port"] = port
    
    # Start API server
    start_api_server(config_data)


def format_text_output(result: ValidationResult) -> str:
    """Format validation result as human-readable text."""
    lines = []
    lines.append(f"Scene Validation Results - {result.scene_id}")
    lines.append("=" * 50)
    lines.append(f"Validation ID: {result.validation_id}")
    lines.append(f"Timestamp: {result.timestamp}")
    lines.append(f"Valid: {'Yes' if result.valid else 'No'}")
    
    if result.errors:
        lines.append("\nErrors:")
        lines.append("-" * 50)
        for i, error in enumerate(result.errors, 1):
            lines.append(f"{i}. {error.error_code}: {error.error_message}")
            if error.element_id:
                lines.append(f"   Element: {error.element_id}")
            if error.severity:
                lines.append(f"   Severity: {error.severity}")
            if error.suggestion:
                lines.append(f"   Suggestion: {error.suggestion}")
            lines.append("")
    
    if result.warnings:
        lines.append("\nWarnings:")
        lines.append("-" * 50)
        for i, warning in enumerate(result.warnings, 1):
            lines.append(f"{i}. {warning.warning_code}: {warning.warning_message}")
            if warning.element_id:
                lines.append(f"   Element: {warning.element_id}")
            if warning.suggestion:
                lines.append(f"   Suggestion: {warning.suggestion}")
            lines.append("")
    
    if result.performance_metrics:
        lines.append("\nPerformance Metrics:")
        lines.append("-" * 50)
        for key, value in result.performance_metrics.items():
            lines.append(f"{key}: {value}")
    
    lines.append(f"\nValidation Time: {result.validation_time_ms} ms")
    
    return "\n".join(lines)


if __name__ == "__main__":
    app()
