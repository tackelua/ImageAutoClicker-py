# Auto Clicker with Image Detection

An application that automatically clicks when it finds a matching image on the screen.

## Features

- Select specific screen areas for searching
- Use existing images or crop directly from the screen
- Adjust detection precision (with OpenCV)
- Preview click locations without actually clicking
- Visual feedback with status indicators
- Customizable delay between clicks

## Installation

### Prerequisites

- Python 3.7 or higher
- Pip (Python package installer)

### Option 1: Installation with Virtual Environment (Recommended)

1. Clone this repository:
   ```
   git clone https://github.com/tackelua/ImageAutoClicker-py.git
   cd ImageAutoClicker-with-ImageDetection
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

### Option 2: Direct Installation

1. Clone this repository:
   ```
   git clone https://github.com/tackelua/ImageAutoClicker-py.git
   cd ImageAutoClicker-with-ImageDetection
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

1. Run the application:
   ```
   python auto_clicker.py
   ```
   
   Or use the starter script (which checks dependencies):
   ```
   python starter.py
   ```

2. Select a screen area where the application will search for your target image.

3. Either select an existing image file or crop a new one from the screen.

4. Adjust the settings:
   - Match Precision: Higher for exact matches, lower for more flexible detection (requires OpenCV)
   - Delay: Time in seconds between each search/click
   - Preview Mode: Check to see detection without clicking

5. Click "Start" to begin the automatic detection and clicking.

6. Click "Stop" at any time to stop the process.

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
- Added detailed error reporting

### AI Assistance

The modifications and improvements to this project were implemented with the assistance of Claude AI (Anthropic). The project owner provided requirements and prompts, while Claude helped with code generation, debugging, and documentation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---
© 2025 ImageAutoClicker-py
