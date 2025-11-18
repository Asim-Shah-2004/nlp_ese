"""
Simple test script for the Agentic RAG PDF Chatbot
Run this after installing dependencies to verify everything works
"""

import os
import sys

def test_imports():
    """Test if all required packages are installed."""
    print("Testing imports...")
    
    required_packages = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('google.generativeai', 'Google Generative AI'),
        ('PyPDF2', 'PyPDF2'),
        ('langchain', 'LangChain'),
        ('chromadb', 'ChromaDB'),
        ('sentence_transformers', 'Sentence Transformers'),
        ('pydantic', 'Pydantic'),
        ('dotenv', 'Python Dotenv')
    ]
    
    failed = []
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - Not installed")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    print("\n✅ All packages installed successfully!")
    return True

def test_env_file():
    """Test if .env file exists and has API key."""
    print("\nTesting environment configuration...")
    
    if not os.path.exists('.env'):
        print("⚠ .env file not found")
        print("Copy .env.example to .env and add your Gemini API key")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key or api_key == 'your_gemini_api_key_here':
        print("⚠ GOOGLE_API_KEY not set in .env file")
        print("Add your Gemini API key to the .env file")
        return False
    
    print("✅ Environment configured correctly!")
    return True

def test_directories():
    """Test if required directories exist."""
    print("\nTesting directory structure...")
    
    required_dirs = ['uploads', 'chroma_db']
    for dir_name in required_dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/ exists")
        else:
            os.makedirs(dir_name, exist_ok=True)
            print(f"✓ {dir_name}/ created")
    
    print("✅ Directories ready!")
    return True

def test_modules():
    """Test if custom modules can be imported."""
    print("\nTesting custom modules...")
    
    modules = [
        'config',
        'pdf_processor',
        'vector_store',
        'chat_agent',
        'main'
    ]
    
    failed = []
    for module in modules:
        try:
            __import__(module)
            print(f"✓ {module}.py")
        except Exception as e:
            print(f"✗ {module}.py - {str(e)}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        return False
    
    print("✅ All modules import successfully!")
    return True

def main():
    """Run all tests."""
    print("=" * 60)
    print("Agentic RAG PDF Chatbot - Setup Verification")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Environment", test_env_file()))
    results.append(("Directories", test_directories()))
    results.append(("Modules", test_modules()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    all_passed = all(result[1] for result in results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{name:20s} {status}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n🎉 All tests passed! You're ready to start the server.")
        print("\nRun: python main.py")
        print("Or:  uvicorn main:app --reload")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
