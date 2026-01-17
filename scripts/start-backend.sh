#!/bin/bash

# Script to start the FastAPI backend
# Checks for dependencies and installs if needed
#
# Virtual Environment:
# - Uses root venv (../venv from this script's location)
# - Falls back to backend/venv if root venv doesn't exist
# - Creates venv if needed

cd "$(dirname "$0")/.." || exit 1

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

# Check if root virtual environment exists and is valid
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "🐍 Using root virtual environment..."
    PYTHON_CMD="python"
  else
    # Venv exists but doesn't have packages
    echo "⚠️  Root venv exists but packages missing. Installing..."
    pip install --upgrade pip --quiet
    # Check if requirements.txt is in root or backend
    if [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
    elif [ -f "backend/requirements.txt" ]; then
      pip install -r backend/requirements.txt
    else
      echo "❌ Error: requirements.txt not found!"
      exit 1
    fi
    PYTHON_CMD="python"
  fi
elif [ -d "backend/venv" ] && [ -f "backend/venv/bin/activate" ]; then
  # Fallback to backend/venv if root venv doesn't exist
  source backend/venv/bin/activate
  if python -c "import fastapi, uvicorn" 2>/dev/null; then
    echo "🐍 Using backend virtual environment (backend/venv)..."
    PYTHON_CMD="python"
  else
    echo "⚠️  Backend venv exists but packages missing. Installing..."
    pip install --upgrade pip --quiet
    # Check if requirements.txt is in root or backend
    if [ -f "requirements.txt" ]; then
      pip install -r requirements.txt
    elif [ -f "backend/requirements.txt" ]; then
      pip install -r backend/requirements.txt
    else
      echo "❌ Error: requirements.txt not found!"
      exit 1
    fi
    PYTHON_CMD="python"
  fi
else
  # No venv found, try to find Python with packages installed
  PYTHON_CMD=$(find_python_with_packages)
  
  if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: No Python with packages found!"
    echo "   Please run: python3.12 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
  fi
  
  echo "🐍 Using system Python with packages installed: $PYTHON_CMD"
fi

# Verify packages are available
if ! "$PYTHON_CMD" -c "import fastapi, uvicorn" 2>/dev/null; then
  echo "❌ Error: Required packages (fastapi, uvicorn) are not installed!"
  echo "   Try running: source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

# Run uvicorn using the selected Python (from backend directory)
# Port 8002 to avoid conflict with SAM webui gateway on 8000
echo "🚀 Starting FastAPI backend on http://localhost:8002"
cd backend
"$PYTHON_CMD" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8002

