# ADK Development Environment Setup

## Step-by-Step Setup Guide

### 1. Verify Python Version

```bash
python --version
# Should be Python 3.10 or higher
```

### 2. Create Virtual Environment

```bash
cd adco_project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install ADK

```bash
# Install Google ADK
pip install google-adk

# Or install from source if needed
# pip install git+https://github.com/google/adk.git
```

### 4. Verify Installation

```bash
python -c "import google.adk; print('ADK installed successfully')"
```

### 5. Install ADCO Dependencies

```bash
pip install -r requirements.txt
```

### 6. Test ADK Integration

```bash
# Run test script
python learning/adk/test_adk_setup.py
```

## Troubleshooting

### Issue: ADK not found

**Solution**: Ensure virtual environment is activated and ADK is installed:
```bash
pip list | grep adk
```

### Issue: Import errors

**Solution**: Check Python path and ensure ADK is in the environment:
```bash
python -c "import sys; print(sys.path)"
```

### Issue: Version conflicts

**Solution**: Use a fresh virtual environment and install dependencies in order:
```bash
pip install google-adk
pip install -r requirements.txt
```

## Development Tools

### Recommended IDE Setup

- **VS Code**: Install Python extension
- **PyCharm**: Configure Python interpreter to use venv
- **Jupyter**: For interactive learning and testing

### Useful Commands

```bash
# Activate virtual environment
source venv/bin/activate

# Deactivate virtual environment
deactivate

# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run linting
ruff check adco_project/
```




