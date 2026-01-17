"""
API routes for triggering SAM agents
"""
from fastapi import APIRouter, HTTPException
import httpx
import uuid
from app.core.config import settings

router = APIRouter(prefix="/api/agents", tags=["agents"])

# SAM WebUI Gateway URL (also serves as REST API gateway)
SAM_WEBUI_GATEWAY_URL = "http://localhost:8000"


@router.post("/trigger")
async def trigger_agents():
    print("Triggering agents...")
    """
    Trigger the agent workflow via SAM WebUI Gateway.
    Sends a task to the orchestrator which will coordinate PRAgent and MeetingAgent in parallel,
    then ManagerAgent with both results.
    """
    try:
        # Submit task to SAM WebUI Gateway using JSON-RPC format
        # The orchestrator will handle the workflow: PRAgent + MeetingAgent (parallel) -> ManagerAgent
        async with httpx.AsyncClient(timeout=300.0) as client:
            response = await client.post(
                f"{SAM_WEBUI_GATEWAY_URL}/api/v1/message:send",
                json={
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "message/send",
                    "params": {
                        "message": {
                            "messageId": str(uuid.uuid4()),
                            "role": "user",
                            "kind": "message",
                            "parts": [
                                {
                                    "kind": "text",
                                    "text": "Run the agent workflow: execute PRAgent and MeetingAgent in parallel, then run ManagerAgent with both results."
                                }
                            ],
                            "metadata": {
                                "agent_name": "OrchestratorAgent"
                            }
                        }
                    }
                },
                headers={
                    "Content-Type": "application/json",
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"SAM Gateway error: {response.text}"
                )
            
            result = response.json()
            
            # Extract the response from JSON-RPC result
            # The result contains a Task or Message object
            if "result" in result:
                task_or_message = result["result"]
                # Extract text from message parts or task history
                output_text = ""
                if "history" in task_or_message and task_or_message["history"]:
                    # Get the last message from history
                    last_msg = task_or_message["history"][-1]
                    if "parts" in last_msg:
                        text_parts = [p.get("text", "") for p in last_msg["parts"] if p.get("kind") == "text"]
                        output_text = " ".join(text_parts)
                elif "message" in task_or_message and task_or_message["message"]:
                    msg = task_or_message["message"]
                    if "parts" in msg:
                        text_parts = [p.get("text", "") for p in msg["parts"] if p.get("kind") == "text"]
                        output_text = " ".join(text_parts)
                
                if not output_text:
                    output_text = str(result)
            else:
                output_text = str(result)
            
            return {
                "success": True,
                "result": output_text,
                "raw_response": result
            }
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to SAM WebUI Gateway. Make sure SAM is running on port 8000."
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Request to SAM Gateway timed out. The agents may still be processing."
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error triggering agents: {str(e)}"
        )
