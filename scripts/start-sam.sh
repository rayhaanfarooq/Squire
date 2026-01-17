#!/bin/bash

# Script to start Solace Agent Mesh (SAM)
# This script activates the virtual environment and runs SAM with the required configs
#
# Virtual Environment:
# - Always uses a virtual environment in sam/.venv
# - Never uses system Python to ensure isolation from backend
# - Creates venv if it doesn't exist
# - This is separate from the backend venv (backend/venv)

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}🤖 Starting Solace Agent Mesh (SAM)${NC}"

# Check if SAM directory exists
if [ ! -d "$PROJECT_ROOT/sam" ]; then
  echo -e "${RED}❌ SAM directory not found at $PROJECT_ROOT/sam${NC}"
  exit 1
fi

cd "$PROJECT_ROOT/sam"

# Function to find the best Python executable for SAM venv
find_best_python() {
  # Try python3.12 first
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

# Always use a virtual environment in the sam directory
# Check if virtual environment exists and is valid
if [ -d ".venv" ] && [ -f ".venv/bin/activate" ]; then
  source .venv/bin/activate
  if command -v sam &> /dev/null; then
    echo -e "${GREEN}✅ Using existing SAM virtual environment (sam/.venv)${NC}"
  else
    # Venv exists but SAM is not installed
    echo -e "${YELLOW}⚠️  SAM virtual environment exists but SAM is not installed${NC}"
    echo -e "${BLUE}📦 Installing solace-agent-mesh in SAM venv...${NC}"
    pip install solace-agent-mesh
  fi
else
  # No venv found, create one
  echo -e "${YELLOW}⚠️  SAM virtual environment not found. Creating one...${NC}"
  
  VENV_PYTHON=$(find_best_python)
  if [ -z "$VENV_PYTHON" ]; then
    echo -e "${RED}❌ Error: No Python interpreter found!${NC}"
    exit 1
  fi
  
  if command -v python3.12 &> /dev/null; then
    echo -e "${BLUE}🐍 Creating SAM venv with python3.12...${NC}"
    python3.12 -m venv .venv
  else
    echo -e "${BLUE}🐍 Creating SAM venv with $VENV_PYTHON...${NC}"
    "$VENV_PYTHON" -m venv .venv
  fi
  
  source .venv/bin/activate
  echo -e "${BLUE}📦 Installing solace-agent-mesh in SAM venv...${NC}"
  pip install --upgrade pip --quiet
  pip install solace-agent-mesh
fi

# Ensure we're in the activated venv
if ! command -v sam &> /dev/null; then
  echo -e "${RED}❌ Error: SAM is not installed in the virtual environment!${NC}"
  echo -e "${YELLOW}   Try running: source .venv/bin/activate && pip install solace-agent-mesh${NC}"
  exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
  echo -e "${YELLOW}⚠️  .env file not found in sam/ directory${NC}"
  echo -e "${YELLOW}   Make sure to set LLM_SERVICE_API_KEY and other required variables${NC}"
  echo -e "${YELLOW}   Required variables: LLM_SERVICE_API_KEY, LLM_SERVICE_PLANNING_MODEL_NAME, LLM_SERVICE_GENERAL_MODEL_NAME${NC}"
fi

# Check for required configs
if [ ! -f "configs/webui.yaml" ]; then
  echo -e "${RED}❌ Required config file not found: configs/webui.yaml${NC}"
  exit 1
fi

if [ ! -f "configs/orchestrator.yaml" ]; then
  echo -e "${RED}❌ Required config file not found: configs/orchestrator.yaml${NC}"
  exit 1
fi

# Build the command with configs
CONFIGS="configs/webui.yaml configs/orchestrator.yaml"

# Note: REST gateway (configs/gateways/rest.yaml) requires sam-rest-gateway plugin
# which may not be installed. Commenting out for now.
# If you need REST gateway, install it with: pip install sam-rest-gateway
# if [ -f "configs/gateways/rest.yaml" ]; then
#   CONFIGS="$CONFIGS configs/gateways/rest.yaml"
# fi

# Check for agent configs and add them if they exist
AGENT_COUNT=0
if [ -f "configs/agents/pr-agent.yaml" ]; then
  CONFIGS="$CONFIGS configs/agents/pr-agent.yaml"
  AGENT_COUNT=$((AGENT_COUNT + 1))
fi

if [ -f "configs/agents/meeting-agent.yaml" ]; then
  CONFIGS="$CONFIGS configs/agents/meeting-agent.yaml"
  AGENT_COUNT=$((AGENT_COUNT + 1))
fi

if [ -f "configs/agents/manager-agent.yaml" ]; then
  CONFIGS="$CONFIGS configs/agents/manager-agent.yaml"
  AGENT_COUNT=$((AGENT_COUNT + 1))
fi

if [ $AGENT_COUNT -gt 0 ]; then
  echo -e "${GREEN}✅ Found $AGENT_COUNT agent config(s)${NC}"
fi

echo -e "${GREEN}✅ Starting SAM with configs: $CONFIGS${NC}"
echo ""

# Run SAM
exec sam run $CONFIGS
