# Publishing pyhscodes to PyPI

This guide will walk you through publishing the pyhscodes package to PyPI.

## Prerequisites

1. **Create PyPI Account**: Go to https://pypi.org/account/register/ and create an account
2. **Create TestPyPI Account**: Go to https://test.pypi.org/account/register/ for testing
3. **Generate API Tokens**:
   - Go to https://pypi.org/manage/account/token/ and create a new API token
   - Go to https://test.pypi.org/manage/account/token/ and create a new API token for testing

## Step 1: Install Required Tools

```bash
# Install publishing tools
pip install twine

# Install keyring for secure credential storage (optional)
pip install keyring
```

## Step 2: Test on TestPyPI First (Recommended)

Before publishing to the main PyPI, test on TestPyPI:

```bash
# Upload to TestPyPI
python -m twine upload --repository testpypi dist/*

# When prompted:
# Username: __token__
# Password: your-testpypi-api-token
```

Test the installation from TestPyPI:

```bash
# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ pyhscodes

# Test the package
python -c "import pyhscodes; print(len(pyhscodes.hscodes))"
```

## Step 3: Publish to PyPI

Once you've tested on TestPyPI:

```bash
# Upload to PyPI
python -m twine upload dist/*

# When prompted:
# Username: __token__
# Password: your-pypi-api-token
```

## Step 4: Verify Publication

1. Check your package at: https://pypi.org/project/pyhscodes/
2. Install from PyPI to test:

```bash
pip install pyhscodes
python -c "import pyhscodes; print('Success!')"
```

## Alternative: Using API Tokens in .pypirc

Create `~/.pypirc` file for easier publishing:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-your-api-token-here

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-your-testpypi-api-token-here
```

Then you can publish without entering credentials:

```bash
# Test
twine upload -r testpypi dist/*

# Production
twine upload dist/*
```

## Future Updates

For future versions:

1. Update version in `pyproject.toml`
2. Run tests: `pytest src/pyhscodes/tests/`
3. Build: `python -m build`
4. Upload: `twine upload dist/*`

## Troubleshooting

- **"File already exists"**: You've already uploaded this version. Increment the version number.
- **"Invalid authentication credentials"**: Check your API token is correct.
- **"403 Forbidden"**: You may not have permission to upload to this package name.

## Security Notes

- Never commit API tokens to version control
- Use environment variables or keyring for tokens
- Consider using GitHub Actions for automated publishing 