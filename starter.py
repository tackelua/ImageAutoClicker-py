"""
Starter script for Auto Clicker with Image Detection
"""
import os
import sys
import subprocess

def check_environment():
    """Check if the environment is properly set up"""
    try:
        import PyQt5
        import pyautogui
        from PIL import Image
        try:
            import cv2
            print("✅ OpenCV is installed. Full functionality available.")
        except ImportError:
            print("⚠️ OpenCV is not installed. Some features will be limited.")
            print("To install OpenCV: pip install opencv-python")
        
        print("✅ All core dependencies are installed.")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install all dependencies: pip install -r requirements.txt")
        return False

def ensure_snips_directory():
    """Ensure the snips directory exists"""
    if not os.path.exists("snips"):
        os.makedirs("snips")
        print("✅ Created 'snips' directory for storing images.")
    else:
        print("✅ 'snips' directory already exists.")

def start_application():
    """Start the auto clicker application"""
    print("Starting Auto Clicker with Image Detection...")
    try:
        # Run the module in a separate process to ensure clean exit
        subprocess.run([sys.executable, "auto_clicker.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== Auto Clicker with Image Detection ===")
    if check_environment():
        ensure_snips_directory()
        start_application()
    else:
        print("❌ Environment check failed. Please install required dependencies.")
        sys.exit(1)