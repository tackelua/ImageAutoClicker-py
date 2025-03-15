"""
Auto Run script for Auto Clicker with Image Detection.
This script automatically sets up the environment and runs the application.
"""
import os
import sys
import subprocess
import venv
import platform

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

def setup_venv():
    """Set up a virtual environment if it doesn't exist"""
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print(f"✅ Virtual environment '{venv_dir}' already exists.")
    else:
        print(f"Creating virtual environment in '{venv_dir}'...")
        venv.create(venv_dir, with_pip=True)
        print(f"✅ Virtual environment created in '{venv_dir}'.")
    
    return venv_dir

def get_python_executable(venv_dir):
    """Get the path to the Python executable in the virtual environment"""
    if platform.system() == "Windows":
        return os.path.join(venv_dir, "Scripts", "python.exe")
    else:
        return os.path.join(venv_dir, "bin", "python")

def install_dependencies(venv_dir):
    """Install dependencies in the virtual environment"""
    python_executable = get_python_executable(venv_dir)
    
    print("Installing dependencies in virtual environment...")
    try:
        subprocess.run([python_executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def start_application(venv_dir=None):
    """Start the auto clicker application"""
    print("Starting Auto Clicker with Image Detection...")
    try:
        if venv_dir:
            python_executable = get_python_executable(venv_dir)
        else:
            python_executable = sys.executable
            
        # Run the module in a separate process to ensure clean exit
        subprocess.run([python_executable, "auto_clicker.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=== Auto Clicker with Image Detection ===")
    
    # Check if --no-venv flag is provided
    use_venv = "--no-venv" not in sys.argv
    
    if use_venv:
        print("Setting up virtual environment...")
        venv_dir = setup_venv()
        install_dependencies(venv_dir)
        ensure_snips_directory()
        start_application(venv_dir)
    else:
        print("Using system Python (virtual environment disabled)...")
        if check_environment():
            ensure_snips_directory()
            start_application()
        else:
            print("❌ Environment check failed. Please install required dependencies.")
            sys.exit(1) 