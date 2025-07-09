#!/usr/bin/env python3
"""
Helper script for publishing pyhscodes to PyPI.

Usage:
    python publish.py test    # Upload to TestPyPI
    python publish.py prod    # Upload to PyPI
"""

import subprocess
import sys
import os


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n📦 {description}...")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ["test", "prod"]:
        print("Usage: python publish.py [test|prod]")
        print("  test - Upload to TestPyPI")
        print("  prod - Upload to PyPI")
        sys.exit(1)

    target = sys.argv[1]

    print("🚀 pyhscodes Publishing Script")
    print("=" * 40)

    # Check if dist directory exists
    if not os.path.exists("dist"):
        print("❌ No 'dist' directory found. Please run 'python -m build' first.")
        sys.exit(1)

    # Check if twine is installed
    if not run_command("twine --version", "Checking twine installation"):
        print("❌ Please install twine: pip install twine")
        sys.exit(1)

    # Validate distribution files
    if not run_command("twine check dist/*", "Validating distribution files"):
        sys.exit(1)

    # Upload to appropriate repository
    if target == "test":
        print("\n🧪 Uploading to TestPyPI...")
        print("When prompted, use:")
        print("  Username: __token__")
        print("  Password: your-testpypi-api-token")
        cmd = "twine upload --repository testpypi dist/*"
    else:
        print("\n🌟 Uploading to PyPI...")
        print("When prompted, use:")
        print("  Username: __token__")
        print("  Password: your-pypi-api-token")
        cmd = "twine upload dist/*"

    if run_command(cmd, f"Uploading to {'TestPyPI' if target == 'test' else 'PyPI'}"):
        if target == "test":
            print("\n✅ Upload to TestPyPI successful!")
            print("Test installation with:")
            print("  pip install --index-url https://test.pypi.org/simple/ pyhscodes")
        else:
            print("\n🎉 Upload to PyPI successful!")
            print(
                "Your package is now available at: https://pypi.org/project/pyhscodes/"
            )
            print("Install with: pip install pyhscodes")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
