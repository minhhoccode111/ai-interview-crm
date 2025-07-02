#!/usr/bin/env python3
"""
Setup script for AI Interview CRM Platform
This script helps set up the environment and initialize the database.
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def print_step(step, message):
    """Print a formatted step message"""
    print(f"\n{'='*50}")
    print(f"STEP {step}: {message}")
    print(f"{'='*50}")

def check_python_version():
    """Check if Python version is compatible"""
    print_step(1, "Checking Python Version")
    
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    
    print(f"✅ Python version: {sys.version}")

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist"""
    print_step(2, "Setting Up Virtual Environment")
    
    venv_path = Path("venv")
    
    if venv_path.exists():
        print("✅ Virtual environment already exists")
        return
    
    try:
        subprocess.run([sys.executable, "-m", "venv", "venv"], check=True)
        print("✅ Virtual environment created successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def install_dependencies():
    """Install required dependencies"""
    print_step(3, "Installing Dependencies")
    
    # Determine the correct pip path
    if os.name == 'nt':  # Windows
        pip_path = os.path.join("venv", "Scripts", "pip")
        python_path = os.path.join("venv", "Scripts", "python")
    else:  # Unix/Linux/MacOS
        pip_path = os.path.join("venv", "bin", "pip")
        python_path = os.path.join("venv", "bin", "python")
    
    try:
        # Upgrade pip first
        subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        
        # Install requirements
        subprocess.run([pip_path, "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def setup_environment_file():
    """Create .env file from template"""
    print_step(4, "Setting Up Environment Variables")
    
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if env_file.exists():
        print("✅ .env file already exists")
        return
    
    if env_example.exists():
        # Copy from example
        with open(env_example, 'r') as src, open(env_file, 'w') as dst:
            content = src.read()
            dst.write(content)
        print("✅ .env file created from template")
    else:
        # Create basic .env file
        env_content = """# AI Interview CRM Environment Variables
SECRET_KEY=dev-secret-key-change-in-production-please-use-strong-key
GEMINI_API_KEY=your-gemini-api-key-here
DATABASE_URL=sqlite:///instance/interview.db
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Basic .env file created")
    
    print("\n⚠️  IMPORTANT: Please update the .env file with your actual values:")
    print("   - Set a strong SECRET_KEY")
    print("   - Add your GEMINI_API_KEY from Google AI Studio")

def create_directories():
    """Create necessary directories"""
    print_step(5, "Creating Directory Structure")
    
    directories = [
        "instance",
        "static/uploads",
        "logs"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def initialize_database():
    """Initialize the SQLite database"""
    print_step(6, "Initializing Database")
    
    try:
        # Import Flask app and initialize database
        from app import create_app
        from models.db import db
        
        app = create_app()
        
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Check if tables were created
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Created tables: {', '.join(tables)}")
            
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        sys.exit(1)

def run_tests():
    """Run basic tests to verify setup"""
    print_step(7, "Running Basic Tests")
    
    try:
        # Test imports
        import flask
        import google.generativeai as genai
        import whisper
        print("✅ All required packages can be imported")
        
        # Test app creation
        from app import create_app
        app = create_app()
        
        with app.test_client() as client:
            response = client.get('/api/status')
            if response.status_code == 200:
                print("✅ Flask app is working correctly")
            else:
                print(f"⚠️  Flask app returned status code: {response.status_code}")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Test warning: {e}")
    
    return True

def print_completion_message():
    """Print setup completion message and next steps"""
    print_step(8, "Setup Complete!")
    
    print("""
🎉 AI Interview CRM Platform setup completed successfully!

Next Steps:
1. Update your .env file with the correct GEMINI_API_KEY
   - Visit https://makersuite.google.com/app/apikey to get your key

2. Activate the virtual environment:
   - Windows: venv\\Scripts\\activate
   - Linux/Mac: source venv/bin/activate

3. Start the application:
   python app.py

4. Open your browser to: http://localhost:5000

📚 Documentation:
- README.md for detailed usage instructions
- Check the /api/status endpoint to verify the API is working

🔧 Configuration:
- Database: SQLite (instance/interview.db)
- Upload folder: static/uploads
- Log files: logs/

Happy interviewing! 🚀
    """)

def main():
    """Main setup function"""
    print("🤖 AI Interview CRM Platform Setup")
    print("This script will set up your development environment.\n")
    
    try:
        check_python_version()
        create_virtual_environment()
        install_dependencies()
        setup_environment_file()
        create_directories()
        initialize_database()
        
        if run_tests():
            print_completion_message()
        else:
            print("\n⚠️  Setup completed with warnings. Please check the error messages above.")
    
    except KeyboardInterrupt:
        print("\n\n❌ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Setup failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
