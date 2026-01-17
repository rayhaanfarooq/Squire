1. Create a virtual environment:
python3 -m venv .venv

2. Activate the environment:

On Linux or Unix platforms:

source .venv/bin/activate

On Windows:

.venv\Scripts\activate

3. Install SAM

pip install solace-agent-mesh

4. Ensure installation

sam --version

5. Ensure you have specified the correct variables in .env

LLM_SERVICE_API_KEY=YOUR_API_KEY_HERE
LLM_SERVICE_PLANNING_MODEL_NAME=gpt-5
LLM_SERVICE_GENERAL_MODEL_NAME=gpt-5

6. Run the webui and orchestrator

sam run ./configs/webui.yaml ./configs/orchestrator.yaml