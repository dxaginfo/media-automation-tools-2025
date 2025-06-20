"""Common utility functions for media automation tools."""

import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

def load_json(file_path: str) -> Dict[str, Any]:
    """Load JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {e}")
        return {}

def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """Save data to a JSON file."""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {e}")
        return False

def ensure_directory(directory_path: str) -> bool:
    """Ensure a directory exists, creating it if necessary."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory_path}: {e}")
        return False

def validate_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """Validate data against a schema. Returns list of errors."""
    # Simple schema validation - could be replaced with jsonschema
    errors = []
    for key, expected_type in schema.items():
        if key not in data:
            errors.append(f"Missing required field: {key}")
        elif not isinstance(data[key], expected_type):
            errors.append(f"Field {key} has wrong type. Expected {expected_type.__name__}")
    return errors
