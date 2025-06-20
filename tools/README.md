# Media Automation Tools

This directory contains individual implementations of the media automation tools.

Each tool is contained in its own subdirectory with the following structure:

```
tool-name/
├── README.md           # Tool-specific documentation
├── requirements.txt    # Python dependencies (if applicable)
├── package.json        # Node.js dependencies (if applicable)
├── src/                # Source code
│   ├── main.py or main.js
│   └── ...
├── config/             # Configuration files
│   ├── default.json
│   └── ...
├── examples/           # Example usage
└── tests/              # Tool-specific tests
```

## Tool Index

- **SceneValidator** - Validates scene composition and technical requirements
- **LoopOptimizer** - Optimizes looping media for seamless playback
- **SoundScaffold** - Generates audio scaffolding for video content
- **StoryboardGen** - Generates storyboards from scripts
- **TimelineAssembler** - Assembles timeline from metadata
- **EnvironmentTagger** - Tags environment elements in media
- **ContinuityTracker** - Tracks continuity between scenes
- **VeoPromptExporter** - Exports optimized prompts for Veo
- **FormatNormalizer** - Normalizes media formats for compatibility
- **PostRenderCleaner** - Cleans up artifacts after rendering
