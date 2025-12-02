"""
Setup Test Script

Verifies that all dependencies and configuration are properly set up.
"""

import sys
import os

def test_python_version():
    """Check Python version"""
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ✗ Python {version.major}.{version.minor}.{version.micro} (Need 3.8+)")
        return False

def test_dependencies():
    """Check required dependencies"""
    print("\nChecking dependencies...")

    required = [
        ('selenium', 'Selenium'),
        ('pathlib', 'pathlib'),
    ]

    all_ok = True
    for module, name in required:
        try:
            __import__(module)
            print(f"  ✓ {name} installed")
        except ImportError:
            print(f"  ✗ {name} NOT installed")
            all_ok = False

    return all_ok

def test_chrome():
    """Check Chrome installation"""
    print("\nChecking Google Chrome...")

    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.quit()

        print("  ✓ Chrome and ChromeDriver working")
        return True
    except Exception as e:
        print(f"  ✗ Chrome/ChromeDriver issue: {e}")
        print("    Install Chrome: https://www.google.com/chrome/")
        print("    ChromeDriver should auto-install with webdriver-manager")
        return False

def test_directories():
    """Check directory structure"""
    print("\nChecking directories...")

    dirs = ['src', 'bulk_data']
    files = ['config.json', 'TEMPLATE.md']

    all_ok = True

    for dir_name in dirs:
        if os.path.isdir(dir_name):
            print(f"  ✓ {dir_name}/ exists")
        else:
            print(f"  ✗ {dir_name}/ NOT found")
            all_ok = False

    for file_name in files:
        if os.path.isfile(file_name):
            print(f"  ✓ {file_name} exists")
        else:
            print(f"  ✗ {file_name} NOT found")
            all_ok = False

    return all_ok

def test_markdown_parser():
    """Test markdown parser"""
    print("\nTesting markdown parser...")

    try:
        sys.path.insert(0, 'src')
        from markdown_parser import MarkdownParser

        # Test with TEMPLATE.md
        if os.path.exists('TEMPLATE.md'):
            parser = MarkdownParser('TEMPLATE.md')
            artifacts = parser.parse()
            print(f"  ✓ Markdown parser working ({len(artifacts)} test artifacts found)")
            return True
        else:
            print("  ⚠ TEMPLATE.md not found, skipping parser test")
            return True

    except Exception as e:
        print(f"  ✗ Markdown parser error: {e}")
        return False

def test_file_manager():
    """Test file manager"""
    print("\nTesting file manager...")

    try:
        sys.path.insert(0, 'src')
        from file_manager import FileManager

        fm = FileManager(download_dir='./downloads', artifacts_dir='./artifacts')
        print(f"  ✓ File manager initialized")
        print(f"    Download dir: {fm.download_dir}")
        print(f"    Artifacts dir: {fm.artifacts_dir}")
        return True

    except Exception as e:
        print(f"  ✗ File manager error: {e}")
        return False

def main():
    """Run all tests"""
    print("="*60)
    print("AI Tools GUI Automation - Setup Test")
    print("="*60)

    tests = [
        test_python_version,
        test_dependencies,
        test_directories,
        test_markdown_parser,
        test_file_manager,
        test_chrome
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ✗ Test failed with exception: {e}")
            results.append(False)

    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)

    passed = sum(results)
    total = len(results)

    print(f"Passed: {passed}/{total}")

    if all(results):
        print("\n✓ All tests passed! You're ready to use the tool.")
        print("\nNext steps:")
        print("1. Run: python src/main.py bulk_data/GEMINI_ASSET_PROMPTS.md")
        print("2. Log in to Gemini when prompted")
        print("3. Watch the automation work!")
    else:
        print("\n✗ Some tests failed. Please fix the issues above.")
        print("\nInstallation help:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Install Chrome: https://www.google.com/chrome/")
        print("3. Check SETUP.md for detailed instructions")

    return all(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
