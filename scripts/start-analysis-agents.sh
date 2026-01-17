#!/bin/bash

# Script to start all analysis agents (PR, Meeting, Join, Manager)
# Runs PR Agent, Meeting Agent, Join Agent, and Manager Agent

cd "$(dirname "$0")/.." || exit 1

# Check if root virtual environment exists
if [ -d "venv" ] && [ -f "venv/bin/activate" ]; then
  source venv/bin/activate
  PYTHON_CMD="python"
else
  echo "❌ Error: Root virtual environment not found!"
  echo "   Please run: python3.12 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
  exit 1
fi

echo "🤖 Starting all analysis agents with $PYTHON_CMD..."

# Start all agents in background (from backend directory)
cd backend
$PYTHON_CMD -m app.agents.pr_agent &
PR_AGENT_PID=$!

$PYTHON_CMD -m app.agents.meeting_agent &
MEETING_AGENT_PID=$!

$PYTHON_CMD -m app.agents.join_agent &
JOIN_AGENT_PID=$!

$PYTHON_CMD -m app.agents.manager_agent &
MANAGER_AGENT_PID=$!

echo "✅ All analysis agents started:"
echo "   PR Agent: PID $PR_AGENT_PID"
echo "   Meeting Agent: PID $MEETING_AGENT_PID"
echo "   Join Agent: PID $JOIN_AGENT_PID"
echo "   Manager Agent: PID $MANAGER_AGENT_PID"
echo ""
echo "Workflow: PR Agent + Meeting Agent → Join Agent → Manager Agent"
echo "Trigger via: POST /api/analysis/start"

# Wait for all agents
wait

