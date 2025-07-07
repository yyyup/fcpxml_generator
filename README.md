# FCPXML Generator for DaVinci Resolve

A professional tool that converts cut lists into FCPXML files for seamless import into DaVinci Resolve. No more reel name confusion - uses direct file references for reliable editing workflows.

## Features

### Core Functionality
- **JSON and Text Input**: Load cut lists from JSON files or extract timecodes from text
- **Direct File References**: FCPXML uses exact file paths - no naming conflicts
- **Auto FPS Detection**: Automatically detects frame rate from video files
- **Audio Integration**: Includes synchronized audio tracks
- **Cut Reordering**: Visual interface to rearrange cuts before export

### Multi-Camera Support
- **Synchronized Workflows**: Apply same cuts to multiple camera angles
- **Separate Timelines**: Generates individual FCPXML files for each camera
- **Perfect Sync**: Identical timing across all camera angles
- **Copy/Paste Editing**: Easy to mix clips between camera timelines

### Professional Features
- **Frame-Perfect Accuracy**: Uses source video frame rates for precision
- **Debug Information**: Detailed logs for troubleshooting
- **Batch Processing**: Handle multiple videos with identical cuts
- **Clean Architecture**: Modular codebase for easy maintenance

## Installation

### Option 1: Download Executable (Recommended)
1. Download the latest `.exe` file from releases
2. Run directly - no installation required
3. Works on Windows without Python

### Option 2: Run from Source
```bash
# Clone or download the source code
cd fcpxml_generator

# Run the application
python main.py
```

## Quick Start

### Basic Workflow
1. **Select Input Type**: Choose JSON file or text with timecodes
2. **Load Cut List**: Browse to your cuts file
3. **Select Video**: Choose your source video file
4. **Generate**: Click "Generate FCPXML File"
5. **Import**: In DaVinci Resolve: File → Import → Timeline

### Multi-Camera Workflow
1. **Enable Multi-Camera**: Check "Multi-camera mode"
2. **Load Cut List**: Same cuts will apply to all cameras
3. **Add Videos**: Add multiple camera angles
4. **Generate**: Creates separate FCPXML for each camera
5. **Import All**: Import each FCPXML as separate timeline
6. **Edit**: Copy/paste best shots between timelines

## Input Formats

### JSON Format
```json
[
  { "start": 36.0, "end": 40.0 },
  { "start": 40.0, "end": 50.0 },
  { "start": 60.0, "end": 70.0 }
]
```

### Text Format
```text
Key moments:
• 00:01:20-00:01:35 — Great opening statement
• 00:02:45-00:03:10 — Emotional moment
• 00:04:15-00:04:30 — Perfect sound bite

B-Roll shots:
• 10:30-10:45 — Close-up of hands
• 12:15-12:30 — Wide establishing shot
```

## File Structure

```
fcpxml_generator/
├── main.py                     # Application entry point
├── core/                       # Core functionality
│   ├── fcpxml_generator.py     # FCPXML creation logic
│   ├── timecode_parser.py      # Text/JSON parsing
│   └── video_analyzer.py      # FPS detection
├── gui/                        # User interface
│   └── main_window.py          # Main application window
├── utils/                      # Utilities
│   └── file_helpers.py         # File operations
└── requirements.txt            # Dependencies
```

## Building Executable

### Using PyInstaller
```bash
# Install PyInstaller
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name="FCPXML_Generator" main.py
```

### Using auto-py-to-exe (GUI)
```bash
# Install and run GUI builder
pip install auto-py-to-exe
auto-py-to-exe
```

## Advanced Features

### Frame Rate Detection
- Automatically detects FPS using `ffprobe`
- Supports common rates: 24, 25, 30, 60 fps
- Manual override available
- Fallback to safe defaults

### Cut Management
- **Reorder**: Drag cuts to change timeline order
- **Validate**: Automatic detection of overlaps and issues
- **Preview**: See cut list before generating
- **Debug**: Detailed logs for troubleshooting

### File Management
- **Auto-naming**: Intelligent filename generation
- **Path handling**: Supports complex file paths
- **Validation**: Checks file accessibility
- **Backup**: Optional backup of existing files

## Troubleshooting

### Common Issues

**"Could not detect FPS"**
- Install `ffprobe` (part of FFmpeg)
- Or manually select frame rate

**"File not found in DaVinci"**
- Ensure video file paths are accessible
- Check that files haven't been moved
- Verify file permissions

**"Wrong clips appearing"**
- This doesn't happen with FCPXML! 
- Unlike EDL, FCPXML uses direct file references

### Debug Files
The tool creates `_DEBUG.txt` files with detailed information:
- Source video paths
- Cut timing details
- Frame rate information
- Generation settings

## Development

### Contributing
1. Fork the repository
2. Create feature branch
3. Follow the modular architecture
4. Add tests for new features
5. Submit pull request

### Architecture
- **Separation of Concerns**: UI, logic, and utilities separated
- **Type Hints**: Full type annotation for clarity
- **Error Handling**: Comprehensive exception management
- **Extensibility**: Easy to add new features

## License

MIT License - see LICENSE file for details

## Support

- **Issues**: Report bugs via GitHub issues
- **Features**: Request enhancements via GitHub
- **Documentation**: Check wiki for advanced usage