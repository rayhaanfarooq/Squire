#!/bin/bash

# Script to start the FastAPI backend
# Checks for dependencies and installs if needed
#
# Virtual Environment:
# - Always uses a virtual environment in backend/venv or backend/env
# - Never uses system Python to ensure isolation
# - Creates venv if it doesn't exist

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

# Always use a virtual environment in the backend directory
# Check if virtual environment exists and is valid
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "🐍 Using existing backend virtual environment (backend/venv)..."
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
    echo "🐍 Using existing backend virtual environment (backend/env)..."
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

# If no valid venv, create one (always use venv, never system Python)
if [ -z "$PYTHON_CMD" ]; then
  echo "📦 Creating backend virtual environment..."
  
  # Find best Python to use for venv
  VENV_PYTHON=$(find_best_python)
  
  if [ -z "$VENV_PYTHON" ]; then
    echo "❌ Error: No Python interpreter found!"
    exit 1
  fi
  
  # Try to use python3.12 for venv if available (more compatible)
  if command -v python3.12 &> /dev/null; then
    echo "🐍 Creating backend venv with python3.12..."
    python3.12 -m venv venv
  else
    echo "🐍 Creating backend venv with $VENV_PYTHON..."
    "$VENV_PYTHON" -m venv venv
  fi
  
  source venv/bin/activate
  PYTHON_CMD="python"
  
  echo "📦 Installing backend Python dependencies..."
  pip install --upgrade pip --quiet
  pip install -r requirements.txt
fi

# Verify packages are available
if ! "$PYTHON_CMD" -c "import fastapi, uvicorn" 2>/dev/null; then
  echo "❌ Error: Required packages (fastapi, uvicorn) are not installed!"
  echo "   Try running: pip install -r requirements.txt"
  exit 1
fi

# Run uvicorn using the selected Python
# Port 8002 to avoid conflict with SAM webui gateway on 8000
echo "🚀 Starting FastAPI backend on http://localhost:8002"
"$PYTHON_CMD" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

