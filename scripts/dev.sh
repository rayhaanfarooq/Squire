#!/bin/bash

# Squire Development Script
# Starts both backend and frontend in development mode

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Squire Development Environment${NC}"

# Ensure SQLite database directory exists
DB_DIR="backend/data"
DB_FILE="${DB_DIR}/squire.db"

if [ ! -d "$DB_DIR" ]; then
  echo -e "${YELLOW}📁 Creating SQLite database directory...${NC}"
  mkdir -p "$DB_DIR"
fi

if [ ! -f "$DB_FILE" ]; then
  echo -e "${YELLOW}💾 Creating SQLite database at $DB_FILE${NC}"
  touch "$DB_FILE"
fi

# Check if .env file exists
if [ ! -f "backend/.env" ]; then
  echo -e "${YELLOW}⚠️  backend/.env not found. Creating from .env.example...${NC}"
  if [ -f "backend/.env.example" ]; then
    cp backend/.env.example backend/.env
  else
    echo "ENV=development" > backend/.env
    echo "DATABASE_URL=sqlite:///backend/data/squire.db" >> backend/.env
    echo "SOLACE_HOST=" >> backend/.env
    echo "SOLACE_USERNAME=" >> backend/.env
    echo "SOLACE_PASSWORD=" >> backend/.env
  fi
fi

# Check Python dependencies
echo -e "${BLUE}🐍 Checking Python dependencies...${NC}"
if ! python3 -c "import fastapi" 2>/dev/null; then
  echo -e "${YELLOW}📦 Installing Python dependencies...${NC}"
  cd backend
  pip install -r requirements.txt || pip3 install -r requirements.txt
  cd ..
fi

# Check Node dependencies
echo -e "${BLUE}📦 Checking Node dependencies...${NC}"
if [ ! -d "frontend/node_modules" ]; then
  echo -e "${YELLOW}📦 Installing frontend dependencies...${NC}"
  cd frontend
  npm install
  cd ..
fi

# Check root node_modules for concurrently
if [ ! -d "node_modules" ]; then
  echo -e "${YELLOW}📦 Installing root dependencies (concurrently)...${NC}"
  npm install
fi

echo -e "${GREEN}✅ Dependencies checked${NC}"
echo ""
echo -e "${BLUE}Starting servers:${NC}"
echo -e "${GREEN}  Backend:  http://localhost:8002${NC}"
echo -e "${GREEN}  Frontend: http://localhost:5173${NC}"
echo -e "${GREEN}  SAM:      http://localhost:8000 (webui gateway + REST API)${NC}"
echo ""

# Start both servers using concurrently
npm run dev

