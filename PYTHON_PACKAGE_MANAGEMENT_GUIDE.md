# Python Package Management Best Practices Guide

## Overview
This guide covers best practices for managing Python libraries and packages to avoid potential conflicts, specifically tailored for financial/investment projects like the Hi5 ETF reminder system.

## 1. Virtual Environments (Recommended Approach)

### Why Use Virtual Environments?
- **Isolation**: Each project gets its own Python environment
- **Dependency Management**: Avoid conflicts between different projects
- **Reproducibility**: Ensure consistent environments across different machines
- **Clean System**: Keep your system Python installation clean

### Method 1: Using `venv` (Built-in, Recommended)

```bash
# Navigate to your project directory
cd /home/thanghoang/investment/hiFive

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows (if needed in future)

# Install required packages
pip install pandas yfinance

# Check installed packages
pip list

# Deactivate when done working
deactivate
```

### Method 2: Using `conda` (Alternative)

```bash
# Create environment with specific Python version
conda create -n hi5_etf python=3.11
conda activate hi5_etf

# Install packages
conda install pandas
pip install yfinance  # Some packages may not be available in conda

# List environments
conda env list

# Deactivate
conda deactivate
```

## 2. Dependency Management Tools

### Poetry (Modern, Recommended for New Projects)

```bash
# Install Poetry first
curl -sSL https://install.python-poetry.org | python3 -

# Initialize project (in your project directory)
poetry init

# Add dependencies
poetry add pandas yfinance

# Install all dependencies
poetry install

# Activate shell
poetry shell

# Run your script
python hi5_etf_reminder.py
```

### Pipenv (Alternative)

```bash
# Install pipenv
pip install pipenv

# Install packages (creates Pipfile)
pipenv install pandas yfinance

# Activate environment
pipenv shell

# Install from Pipfile
pipenv install
```

## 3. Requirements Management

### Creating requirements.txt

```bash
# After installing packages in your virtual environment
pip freeze > requirements.txt

# Install from requirements.txt (on new machine or environment)
pip install -r requirements.txt
```

### Sample requirements.txt for Hi5 ETF Project

```txt
# Core dependencies for Hi5 ETF Reminder
pandas==2.0.3
yfinance==0.2.18

# Optional: Development dependencies
# pytest==7.4.0        # For testing
# black==23.7.0         # Code formatting
# flake8==6.0.0         # Linting
```

### Pin Specific Versions (Production)

```txt
# Pin exact versions for production stability
pandas==2.0.3
yfinance==0.2.18
numpy==1.24.3
requests==2.31.0
```

### Flexible Versions (Development)

```txt
# Allow minor updates for development
pandas>=2.0.0,<3.0.0
yfinance>=0.2.0,<0.3.0
```

## 4. Project Structure Best Practices

```
/home/thanghoang/investment/hiFive/
├── venv/                    # Virtual environment (don't commit to git)
├── hi5_etf_reminder.py     # Main script
├── requirements.txt        # Dependencies
├── .gitignore             # Git ignore file
├── README.md              # Project documentation
├── hi5_state.json         # State file (created by script)
└── logs/                  # Optional: log files
```

### Sample .gitignore

```gitignore
# Virtual environments
venv/
env/
.venv/

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# IDE files
.vscode/
.idea/
*.swp

# OS files
.DS_Store
Thumbs.db

# Project specific
hi5_state.json
logs/
```

## 5. Advanced Dependency Management

### Using pip-tools

```bash
# Install pip-tools
pip install pip-tools

# Create requirements.in (high-level dependencies)
echo "pandas" > requirements.in
echo "yfinance" >> requirements.in

# Generate pinned requirements.txt
pip-compile requirements.in

# Install
pip-sync requirements.txt
```

### Version Conflicts Resolution

```bash
# Check for dependency conflicts
pip check

# Show dependency tree
pip install pipdeptree
pipdeptree

# Update packages safely
pip list --outdated
pip install --upgrade pandas yfinance
```

## 6. Docker Approach (For Complete Isolation)

### Dockerfile for Hi5 ETF Project

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directory for state file
RUN mkdir -p /app/data

# Run the application
CMD ["python", "hi5_etf_reminder.py"]
```

### Docker Compose (Optional)

```yaml
version: '3.8'
services:
  hi5-etf:
    build: .
    volumes:
      - ./data:/app/data
    environment:
      - TZ=America/New_York
    restart: unless-stopped
```

## 7. Best Practices Summary

### DO:
- ✅ **Always use virtual environments** for each project
- ✅ **Pin dependency versions** in production (requirements.txt)
- ✅ **Use `.gitignore`** to exclude virtual environments from version control
- ✅ **Document dependencies** clearly
- ✅ **Test after dependency updates**
- ✅ **Use `pip check`** to verify no conflicts
- ✅ **Keep requirements.txt updated**

### DON'T:
- ❌ Install packages globally without virtual environments
- ❌ Commit virtual environment folders to git
- ❌ Use `sudo pip install` (can break system Python)
- ❌ Mix conda and pip carelessly
- ❌ Ignore dependency version conflicts

## 8. Specific Steps for Your Hi5 ETF Project

### Initial Setup (Run Once)

```bash
# 1. Navigate to project directory
cd /home/thanghoang/investment/hiFive

# 2. Create virtual environment
python -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install required packages
pip install pandas yfinance

# 5. Create requirements.txt
pip freeze > requirements.txt

# 6. Create .gitignore (if using git)
cat > .gitignore << EOF
venv/
__pycache__/
*.pyc
hi5_state.json
EOF
```

### Daily Usage

```bash
# Activate environment
source venv/bin/activate

# Run your script
python hi5_etf_reminder.py

# Deactivate when done
deactivate
```

### Adding New Dependencies

```bash
# Activate environment
source venv/bin/activate

# Install new package
pip install requests

# Update requirements.txt
pip freeze > requirements.txt
```

## 9. Troubleshooting Common Issues

### Issue: ImportError after installing package
```bash
# Solution: Ensure virtual environment is activated
source venv/bin/activate
pip list  # Verify package is installed
```

### Issue: Different behavior on different machines
```bash
# Solution: Use exact version pinning
pip freeze > requirements.txt
# Share requirements.txt with others
```

### Issue: Package conflicts
```bash
# Solution: Check for conflicts and resolve
pip check
pipdeptree --warn conflict
```

## 10. Monitoring and Maintenance

### Regular Maintenance Tasks

```bash
# Check for outdated packages
pip list --outdated

# Update packages (test thoroughly after)
pip install --upgrade pandas yfinance

# Check for security vulnerabilities
pip install safety
safety check

# Update requirements.txt after changes
pip freeze > requirements.txt
```

### Automated Dependency Updates

Consider using tools like:
- **Dependabot** (GitHub)
- **pip-review**: `pip install pip-review && pip-review --local --auto`
- **pip-upgrader**: `pip install pip-upgrader && pip-upgrade`

## Conclusion

For your Hi5 ETF reminder project, the recommended approach is:

1. **Use `venv`** for virtual environment management
2. **Pin exact versions** in `requirements.txt` for stability
3. **Document dependencies** clearly
4. **Test thoroughly** after any dependency changes
5. **Keep the environment isolated** from system Python

This approach will ensure your financial script runs reliably and consistently across different environments and time periods.

---

*Last updated: July 2025*
*Project: Hi5 ETF Investment Reminder System*
