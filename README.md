# AutoClicker with Image Detection

Automatically finds and clicks images on your screen.

## Quick Setup

### Option 1: Using starter.py (Recommended)
```
python starter.py
```

### Option 2: Manual Setup
```
# Install required libraries
pip install pyautogui pillow PyQt5
# Run the application
python auto_clicker.py
```

## How to Use

1. **Select Screen Area**
   - Click the "Select Screen Area" button
   - Drag mouse to select the area to search
   - Release to confirm

2. **Select Target Image**
   - Option A: Click "Select Image File" to choose an image from your computer
   - Option B: Click "Crop from Screen" to select an image directly from your screen

3. **Set and Go**
   - Set delay time in seconds
   - Click "Start" to begin searching and clicking
   - Click "Stop" to end the process

## Troubleshooting

- If image detection fails, try selecting a clearer image or a larger search area
- Ensure cropped areas are at least 10x10 pixels
- The search continues until you click "Stop"

## Development Notes

- The application will automatically create a `snips` directory to store temporary images when needed
- The `snips` directory is added to `.gitignore` and should not be included in source control

## Credits and License

This project is a modified version of [AutoClicker-with-ImageDetection](https://github.com/MarkPengJZ/AutoClicker-with-ImageDetection) by MarkPengJZ.

Modifications include:
- English translation of the user interface
- Improved code organization and error handling
- Better handling of temporary files
- Added development tools and documentation

### AI Assistance

The modifications and improvements to this project were implemented with the assistance of Claude AI (Anthropic). The project owner provided requirements and prompts, while Claude helped with code generation, debugging, and documentation.

## License

This project is distributed under the MIT License. See the LICENSE file for details.

---
© 2025 ImageAutoClicker-py
