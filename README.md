# Auto Clicker with Image Detection

An application that automatically clicks when it finds a matching image on the screen.

## Features

- Select specific screen areas for searching
- **Support for multiple target images** - click on whichever is found first
- Use existing images or crop directly from the screen
- Adjust detection precision (with OpenCV)
- Preview click locations without actually clicking
- Return mouse to original position after clicking
- Visual feedback with status indicators
- Customizable delay between clicks
- **Auto-save and restore settings** between sessions

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)

### Option 1: Automatic Installation with Starter Script (Recommended)

The easiest way to get started is to use the starter script, which automatically:
- Creates a virtual environment
- Installs all dependencies
- Ensures all directories are created
- Runs the application

1. Clone this repository:
   ```
   git clone https://github.com/tackelua/ImageAutoClicker-py.git
   cd ImageAutoClicker-py
   ```

2. Run the starter script:
   ```
   python starter.py
   ```

That's it! The starter script will set up everything automatically.

### Option 2: Manual Installation with Virtual Environment

1. Clone this repository:
   ```
   git clone https://github.com/tackelua/ImageAutoClicker-py.git
   cd ImageAutoClicker-py
   ```

2. Create and activate a virtual environment:
   ```
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

### Option 3: Direct Installation (System Python)

1. Clone this repository:
   ```
   git clone https://github.com/tackelua/ImageAutoClicker-py.git
   cd ImageAutoClicker-py
   ```

2. Install dependencies:
   ```
   pip install PyQt5 pyautogui Pillow
   ```

3. Optional: Install OpenCV for enhanced image detection:
   ```
   pip install opencv-python
   ```

## Usage

### Using the Starter Script (Recommended)

Simply run:
```
python starter.py
```

This will set up the environment and start the application automatically.

If you want to use your system Python instead of a virtual environment:
```
python starter.py --no-venv
```

### Running Directly

If you've already set up the environment manually:

1. Run the application:
   ```
   python auto_clicker.py
   ```

2. Select a screen area where the application will search for your target image.

3. **Add one or more target images** either by selecting existing image files or cropping directly from the screen.

4. Adjust the settings:
   - Match Precision: Higher for exact matches (default: 0.8), lower for more flexible detection (requires OpenCV)
   - Delay: Time in seconds between each search/click
   - Preview Mode: Check to see detection without clicking
   - Return Mouse Position: Enable/disable returning mouse to original position after clicking

5. Click "Start" to begin the automatic detection and clicking.

6. Click "Stop" at any time to stop the process.

7. **Your settings and target images will be automatically saved** and restored the next time you run the application.

## Troubleshooting

- **"Confidence" keyword error**: Install OpenCV with `pip install opencv-python`
- **Image not detected**: Try lowering the precision value or ensuring the screen area is correctly selected
- **Clicking wrong position**: Make sure the cropped image doesn't have borders or background elements

## Credits and License

This project is based on the original work by [Mark Peng (MarkPengJZ)](https://github.com/MarkPengJZ/AutoClicker-with-ImageDetection) with the following improvements:

- Enhanced UI with better visual feedback
- Added support for OpenCV-based image detection with adjustable precision
- Fixed image cropping issues (removing borders from selection)
- Added preview mode
- Added return mouse feature
- **Added support for multiple target images**
- **Added auto-save and restore settings**
- Added detailed error reporting

### AI Assistance

The modifications and improvements to this project were implemented with the assistance of Claude AI (Anthropic). The project owner provided requirements and prompts, while Claude helped with code generation, debugging, and documentation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
© 2025 ImageAutoClicker-py
