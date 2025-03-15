"""
Build script for creating a standalone executable of Auto Clicker with Image Detection
"""
import os
import sys
import subprocess
import platform
import venv

def get_python_executable(venv_dir=None):
    """Get the path to the Python executable, using virtual environment if provided"""
    if venv_dir:
        if platform.system() == "Windows":
            return os.path.join(venv_dir, "Scripts", "python.exe")
        else:
            return os.path.join(venv_dir, "bin", "python")
    else:
        return sys.executable

def setup_venv():
    """Set up a virtual environment for building"""
    venv_dir = "venv"
    if os.path.exists(venv_dir):
        print(f"✅ Virtual environment '{venv_dir}' already exists.")
    else:
        print(f"Creating virtual environment in '{venv_dir}'...")
        venv.create(venv_dir, with_pip=True)
        print(f"✅ Virtual environment created in '{venv_dir}'.")
    
    return venv_dir

def ensure_snips_directory():
    """Ensure the snips directory exists"""
    if not os.path.exists("snips"):
        os.makedirs("snips")
        print("✅ Created 'snips' directory for storing images.")
    else:
        print("✅ 'snips' directory already exists.")

def install_dependencies(venv_dir=None):
    """Install dependencies for building"""
    python_executable = get_python_executable(venv_dir)
    
    print("Installing dependencies...")
    try:
        subprocess.run([python_executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Core dependencies installed successfully.")
        
        # Check if PyInstaller is installed
        try:
            subprocess.run([python_executable, "-m", "PyInstaller", "--version"], 
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            print("✅ PyInstaller is already installed.")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("Installing PyInstaller...")
            subprocess.run([python_executable, "-m", "pip", "install", "pyinstaller"], check=True)
            print("✅ PyInstaller installed successfully.")
            
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        return False

def build_executable(venv_dir=None):
    """Build the application into an executable file"""
    try:
        python_executable = get_python_executable(venv_dir)
        
        # Build the executable
        print("Building executable file... This may take a few minutes.")
        
        # Use --add-data to include the 'snips' directory
        spec_file = "auto_clicker.spec"
        
        # Check if spec file already exists
        if os.path.exists(spec_file):
            print(f"Using existing spec file: {spec_file}")
            build_cmd = [python_executable, "-m", "PyInstaller", spec_file]
        else:
            print("Creating new PyInstaller configuration...")
            # Determine the separator for paths based on platform
            separator = os.pathsep
            build_cmd = [
                python_executable, "-m", "PyInstaller",
                "--name=ImageAutoClicker",
                "--onefile",
                "--windowed",
                "--add-data", f"snips{separator}snips",
                "auto_clicker.py"
            ]
        
        subprocess.run(build_cmd, check=True)
        
        # Path to the generated executable
        dist_dir = "dist"
        if platform.system() == "Windows":
            exe_path = os.path.join(dist_dir, "ImageAutoClicker.exe")
        else:
            exe_path = os.path.join(dist_dir, "ImageAutoClicker")
        
        if os.path.exists(exe_path):
            print(f"✅ Executable built successfully: {exe_path}")
            print(f"Now you can run the application directly by double-clicking {os.path.basename(exe_path)}")
            return True
        else:
            print("⚠️ Executable not found at expected location. Check the 'dist' directory.")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Error building executable: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during build: {e}")
        return False

if __name__ == "__main__":
    print("=== Building Auto Clicker with Image Detection ===")
    
    # Check if --no-venv flag is provided
    use_venv = "--no-venv" not in sys.argv
    
    if use_venv:
        print("Setting up virtual environment for building...")
        venv_dir = setup_venv()
        if install_dependencies(venv_dir):
            ensure_snips_directory()
            build_executable(venv_dir)
        else:
            print("❌ Failed to install dependencies. Aborting build.")
            sys.exit(1)
    else:
        print("Using system Python (virtual environment disabled)...")
        if install_dependencies():
            ensure_snips_directory()
            build_executable()
        else:
            print("❌ Failed to install dependencies. Aborting build.")
            sys.exit(1)

    print("\nBuild process completed!")
    print("If successful, you should find the executable in the 'dist' folder.") 