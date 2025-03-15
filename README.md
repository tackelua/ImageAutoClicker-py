# Auto Clicker with Image Detection

An application that automatically clicks when it finds a matching image on the screen.

## Features

- Select specific screen areas for searching
- Support for multiple target images (click on whichever is found first)
- Multiple delay options (between searches, before click, after image found)
- Adjust detection precision with OpenCV (optional)
- Preview mode without clicking
- Auto-save and restore all settings

## Quick Start

### Option 1: Run with Python (Recommended)

```bash
# Clone repository
git clone https://github.com/tackelua/ImageAutoClicker-py.git
cd ImageAutoClicker-py

# Run auto-setup script
python auto_run.py
```

### Option 2: Standalone Executable

1. Download from Releases or build with:
   ```
   python build.py
   ```

2. Run `dist/ImageAutoClicker.exe` (Windows) or `dist/ImageAutoClicker` (Linux/macOS)

## Requirements

- Python 3.7+
- Dependencies: PyQt5, pyautogui, Pillow
- Optional: OpenCV for better image matching

## Basic Usage

1. Run with `python auto_clicker.py` or use the auto-run script
2. Select screen search area
3. Add one or more target images
4. Adjust settings:
   - Match precision (higher = more accurate, lower = more matches)
   - Delay times
   - Click options (preview mode, return mouse position)
5. Click Start/Stop to control the process

## Troubleshooting

- **Image not detected**: Try lowering precision or check search area
- **Clicking wrong position**: Ensure cropped image is clean without borders
- **Executable issues**: Try running from command line to see error messages

## Credits

This project is based on the original work by [MarkPengJZ](https://github.com/MarkPengJZ/AutoClicker-with-ImageDetection) with enhancements for multiple target images and better UI.

## License

MIT License - See LICENSE file for details.

---
© 2023 ImageAutoClicker-py
