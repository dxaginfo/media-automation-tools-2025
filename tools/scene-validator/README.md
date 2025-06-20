# SceneValidator

SceneValidator is a tool designed to validate scene composition and technical requirements for media production. It checks scene descriptions against predefined rules and provides detailed feedback on compliance and suggested improvements.

## Features

- Validates scene composition against defined rules
- Provides detailed error and warning reports
- Integrates with Gemini API for intelligent validation
- Supports Google Cloud services for storage and processing
- Offers multiple interfaces: API, CLI, and web upload

## Getting Started

### Prerequisites

- Python 3.9+
- Google Cloud account with appropriate permissions
- Gemini API access

### Installation

```bash
pip install -r requirements.txt
export GOOGLE_APPLICATION_CREDENTIALS="path/to/credentials.json"
```

### Configuration

Copy the example configuration and modify as needed:

```bash
cp config.example.json config.json
```

### Usage

```bash
# Command-line usage
python -m scene_validator --config config.json --scene path/to/scene.json

# API usage
from scene_validator import SceneValidator

validator = SceneValidator(config_path='config.json')
result = validator.validate_from_file('path/to/scene.json')
```

## Input Schema

See the documentation for details on the input schema format.

## Output Schema

See the documentation for details on the output schema format.

## Development

```bash
# Run tests
python -m pytest

# Check code style
python -m flake8
```
