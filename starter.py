import subprocess
import sys
import os

# Python environment information
print(f"Python Version: {sys.version}")
print(f"Python Path: {sys.executable}")

# We don't create the snips directory here anymore
# It will be created when needed during application usage

# Check required modules
modules_to_check = ['pyautogui', 'PIL', 'PyQt5']
missing_modules = []

for module in modules_to_check:
    try:
        __import__(module)
        print(f"Module {module} is installed.")
    except ImportError:
        missing_modules.append(module)
        print(f"Module {module} is NOT installed.")

# Install missing modules
if missing_modules:
    print("\nInstalling missing modules...")
    module_install_cmd = [sys.executable, "-m", "pip", "install"] + missing_modules
    result = subprocess.run(module_install_cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.returncode != 0:
        print(f"Error installing modules: {result.stderr}")
        sys.exit(1)
    else:
        print("Successfully installed all required modules.")

# Launch the main application
print("\nLaunching auto_clicker.py...")
try:
    subprocess.run([sys.executable, "auto_clicker.py"])
except Exception as e:
    print(f"Error running auto_clicker.py: {e}")