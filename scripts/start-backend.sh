#!/bin/bash

# Script to start the FastAPI backend
# Checks for dependencies and installs if needed

cd "$(dirname "$0")/../backend" || exit 1

# Function to find the best Python executable
find_best_python() {
  # Try python3.12 first (where packages are likely installed)
  if command -v python3.12 &> /dev/null; then
    if python3.12 -c "import sys; sys.exit(0)" 2>/dev/null; then
      echo "python3.12"
      return 0
    fi
  fi
  
  # Try python3
  if command -v python3 &> /dev/null; then
    if python3 -c "import sys; sys.exit(0)" 2>/dev/null; then
      echo "python3"
      return 0
    fi
  fi
  
  # Try python
  if command -v python &> /dev/null; then
    if python -c "import sys; sys.exit(0)" 2>/dev/null; then
      echo "python"
      return 0
    fi
  fi
  
  return 1
}

# Function to find Python that has required packages
find_python_with_packages() {
  # Try python3.12 first (where packages are installed)
  if python3.12 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "python3.12"
    return 0
  fi
  
  # Try python3
  if python3 -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "python3"
    return 0
  fi
  
  # Try python
  if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "python"
    return 0
  fi
  
  return 1
}

# Check if virtual environment exists and is valid
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "🐍 Using existing virtual environment..."
    PYTHON_CMD="python"
  else
    # Venv exists but doesn't have packages, remove it
    echo "🐍 Removing invalid virtual environment..."
    rm -rf venv
    PYTHON_CMD=""
  fi
elif [ -d "env" ] && [ -f "env/bin/activate" ]; then
  source env/bin/activate
  if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "🐍 Using existing virtual environment..."
    PYTHON_CMD="python"
  else
    # Venv exists but doesn't have packages, remove it
    echo "🐍 Removing invalid virtual environment..."
    rm -rf env
    PYTHON_CMD=""
  fi
else
  PYTHON_CMD=""
fi

# If no valid venv, try to use Python with packages installed
if [ -z "$PYTHON_CMD" ]; then
  PYTHON_CMD=$(find_python_with_packages)
  
  if [ -n "$PYTHON_CMD" ]; then
    echo "🐍 Using system Python with packages installed: $PYTHON_CMD"
  else
    # No Python with packages found, create venv
    echo "📦 No Python with packages found. Creating virtual environment..."
    
    # Find best Python to use for venv (prefer 3.12 over 3.13)
    VENV_PYTHON=$(find_best_python)
    
    if [ -z "$VENV_PYTHON" ]; then
      echo "❌ Error: No Python interpreter found!"
      exit 1
    fi
    
    # Try to use python3.12 for venv if available (more compatible)
    if command -v python3.12 &> /dev/null; then
      echo "🐍 Creating venv with python3.12..."
      python3.12 -m venv venv
    else
      echo "🐍 Creating venv with $VENV_PYTHON..."
      "$VENV_PYTHON" -m venv venv
    fi
    
    source venv/bin/activate
    PYTHON_CMD="python"
    
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip --quiet
    pip install -r requirements.txt
  fi
fi

# Verify packages are available
if ! "$PYTHON_CMD" -c "import fastapi, uvicorn" 2>/dev/null; then
  echo "❌ Error: Required packages (fastapi, uvicorn) are not installed!"
  echo "   Try running: pip install -r requirements.txt"
  exit 1
fi

# Run uvicorn using the selected Python
echo "🚀 Starting FastAPI backend on http://localhost:8000"
"$PYTHON_CMD" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

