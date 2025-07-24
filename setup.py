#!/usr/bin/env python3
"""
Setup script for Battery SDL1 Workflow Mapper

This script helps with installation and setup of the SDL1 system.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version}")
    return True

def check_directory_structure():
    """Verify the directory structure is correct"""
    required_dirs = ['src', 'tests', 'docs', 'data']
    required_files = [
        'src/workflow_mapper.py',
        'src/sdl1_operations.py', 
        'src/opentrons_functions.py',
        'src/api_server.py',
        'tests/final_integration_test.py',
        'docs/README.md',
        'data/test_workflow-1753364156528.json'
    ]
    
    print("🔍 Checking directory structure...")
    
    missing_dirs = []
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            missing_dirs.append(dir_name)
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ Directory structure is correct")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    if not os.path.exists('requirements.txt'):
        print("⚠️  requirements.txt not found, creating basic requirements...")
        with open('requirements.txt', 'w') as f:
            f.write("""# Core dependencies
fastapi>=0.68.0
uvicorn>=0.15.0
pydantic>=1.8.0
requests>=2.25.0

# Optional dependencies (install manually if needed)
# opentrons>=6.0.0
# pandas>=1.3.0
# numpy>=1.21.0

# Development dependencies
# pytest>=6.0.0
# pytest-asyncio>=0.15.0
""")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("💡 Try installing manually: pip install -r requirements.txt")
        return False

def run_basic_tests():
    """Run basic tests to verify setup"""
    print("🧪 Running basic tests...")
    
    test_files = [
        'tests/test_json_compatibility.py',
        'tests/final_integration_test.py'
    ]
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"Running {test_file}...")
            try:
                result = subprocess.run(
                    [sys.executable, test_file],
                    capture_output=True,
                    text=True,
                    timeout=60,
                    cwd='tests' if test_file.startswith('tests/') else '.'
                )
                
                if result.returncode == 0:
                    print(f"✅ {test_file} passed")
                else:
                    print(f"❌ {test_file} failed")
                    print(f"Error: {result.stderr}")
                    return False
            except Exception as e:
                print(f"❌ Error running {test_file}: {e}")
                return False
    
    print("✅ Basic tests completed successfully")
    return True

def create_run_scripts():
    """Create convenient run scripts"""
    print("📝 Creating run scripts...")
    
    # Create run_tests.sh for Unix systems
    with open('run_tests.sh', 'w') as f:
        f.write("""#!/bin/bash
# Run all tests for Battery SDL1 system

echo "🧪 Running Battery SDL1 Test Suite"
cd tests/
python run_tests.py
""")
    
    # Make it executable
    try:
        os.chmod('run_tests.sh', 0o755)
    except:
        pass  # Windows doesn't support chmod
    
    # Create run_tests.bat for Windows
    with open('run_tests.bat', 'w') as f:
        f.write("""@echo off
REM Run all tests for Battery SDL1 system

echo Running Battery SDL1 Test Suite
cd tests
python run_tests.py
pause
""")
    
    # Create start_server script
    with open('start_server.py', 'w') as f:
        f.write("""#!/usr/bin/env python3
\"\"\"
Start the Battery SDL1 API Server
\"\"\"

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

try:
    from api_server import app
    import uvicorn
    
    print("🚀 Starting Battery SDL1 API Server...")
    print("📡 Server will be available at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("🛑 Press Ctrl+C to stop")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
except ImportError as e:
    print(f"❌ Failed to start server: {e}")
    print("💡 Make sure FastAPI and uvicorn are installed:")
    print("   pip install fastapi uvicorn")
    sys.exit(1)
except Exception as e:
    print(f"❌ Server error: {e}")
    sys.exit(1)
""")
    
    print("✅ Run scripts created")
    return True

def main():
    """Main setup function"""
    print("🔧 Battery SDL1 Workflow Mapper Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check directory structure
    if not check_directory_structure():
        print("💡 Make sure you're running this from the repository root")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("⚠️  Continuing without installing dependencies")
    
    # Create run scripts
    create_run_scripts()
    
    # Run basic tests
    if not run_basic_tests():
        print("⚠️  Some tests failed, but setup is complete")
    
    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("  1. Run tests: python tests/run_tests.py")
    print("  2. Start server: python start_server.py")
    print("  3. Check docs: open docs/INDEX.md")
    print("  4. View sample data: ls data/")
    
    print("\n💡 Quick test:")
    print("  cd tests && python final_integration_test.py")

if __name__ == "__main__":
    main()
