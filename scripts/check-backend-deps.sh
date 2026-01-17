#!/bin/bash

# Script to check if Python dependencies are installed
# Returns 0 if installed, 1 if not

cd "$(dirname "$0")/.." || exit 1

# Check if virtual environment exists
if [ -d "backend/venv" ] || [ -d "backend/env" ]; then
  # If venv exists, check if uvicorn is installed in it
  if [ -d "backend/venv" ]; then
    source backend/venv/bin/activate 2>/dev/null
  elif [ -d "backend/env" ]; then
    source backend/env/bin/activate 2>/dev/null
  fi
fi

# Check if uvicorn is installed
if command -v uvicorn &> /dev/null; then
  exit 0
fi

# Try python3 -m uvicorn
if python3 -m uvicorn --version &> /dev/null || python -m uvicorn --version &> /dev/null; then
  exit 0
fi

exit 1

