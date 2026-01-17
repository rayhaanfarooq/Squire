"""
API routes for triggering SAM agents
"""
from fastapi import APIRouter, HTTPException
import httpx
import asyncio
from app.core.config import settings

router = APIRouter(prefix="/api/agents", tags=["agents"])

# SAM REST Gateway URL (REST API Gateway plugin)
SAM_REST_GATEWAY_URL = "http://localhost:8080"


@router.post("/trigger")
async def trigger_agents():
    print("Triggering agents...")
    """
    Trigger the agent workflow via SAM REST Gateway (v2 async API).
    Sends a task to the orchestrator which will coordinate PRAgent and MeetingAgent in parallel,
    then ManagerAgent with both results.
    Uses the async pattern: POST /api/v2/tasks -> GET /api/v2/tasks/{taskId} (polling)
    """
    try:
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Step 1: Submit task to REST Gateway (v2 async API)
            # Returns 202 Accepted with taskId
            # REST Gateway v2 API expects multipart/form-data, not JSON
            submit_response = await client.post(
                f"{SAM_REST_GATEWAY_URL}/api/v2/tasks",
                data={
                    "agent_name": "OrchestratorAgent",
                    "prompt": "Please coordinate the following workflow: 1) Ask PRAgent to 'perform PR analysis'. 2) Ask MeetingAgent to 'perform meeting analysis'. Run these two requests in parallel. 3) Once both agents have completed, take their results and ask ManagerAgent to synthesize the results from both PRAgent and MeetingAgent. Return the final result from ManagerAgent.",
                },
            )
            
            if submit_response.status_code == 202:
                # Async pattern: Get taskId from response
                task_data = submit_response.json()
                task_id = task_data.get("taskId")
                
                if not task_id:
                    raise HTTPException(
                        status_code=500,
                        detail="No taskId returned from SAM Gateway"
                    )
                
                # Step 2: Poll for task completion
                # REST Gateway returns 202 while task is running, 200 when complete
                max_polls = 180  # Poll up to 180 times (9 minutes for long-running tasks)
                poll_interval = 3.0  # 3 seconds between polls (less frequent polling)
                
                print(f"Polling for task {task_id} (max {max_polls} polls, {poll_interval}s interval)...")
                
                for poll_count in range(max_polls):
                    # Sleep before polling (except first poll - check immediately)
                    if poll_count > 0:
                        await asyncio.sleep(poll_interval)
                    
                    if poll_count % 10 == 0 and poll_count > 0:  # Log every 10th poll (every 30 seconds)
                        print(f"Poll {poll_count + 1}/{max_polls} for task {task_id} (waiting for agents to complete)...")
                    
                    status_response = await client.get(
                        f"{SAM_REST_GATEWAY_URL}/api/v2/tasks/{task_id}",
                        headers={
                            "Content-Type": "application/json",
                        }
                    )
                    
                    # 202 Accepted = task still running, continue polling
                    if status_response.status_code == 202:
                        # Try to get status info even from 202 response if available
                        try:
                            status_data = status_response.json()
                            if "status" in status_data:
                                state = status_data.get("status", {}).get("state", "working")
                                if state == "working":
                                    # Task is actively working or paused waiting for sub-agents
                                    pass  # Continue polling
                        except:
                            pass  # If we can't parse, just continue
                        continue
                    
                    # 200 OK = task completed, check the result
                    if status_response.status_code == 200:
                        task_status = status_response.json()
                        state = task_status.get("status", {}).get("state", "unknown")
                        
                        # Extract response text from status.message.parts
                        output_text = ""
                        status_obj = task_status.get("status", {})
                        
                        if "message" in status_obj and "parts" in status_obj["message"]:
                            # Extract text from message parts
                            text_parts = [
                                p.get("text", "") 
                                for p in status_obj["message"]["parts"] 
                                if p.get("kind") == "text"
                            ]
                            output_text = " ".join(text_parts).strip()
                        
                        # Fallback: check history if available
                        if not output_text and "history" in task_status and task_status["history"]:
                            last_msg = task_status["history"][-1]
                            if "parts" in last_msg:
                                text_parts = [
                                    p.get("text", "") 
                                    for p in last_msg["parts"] 
                                    if p.get("kind") == "text"
                                ]
                                output_text = " ".join(text_parts).strip()
                        
                        # Final fallback
                        if not output_text:
                            output_text = f"Task {state}. See raw_response for details."
                        
                        return {
                            "success": state == "completed",
                            "result": output_text,
                            "task_id": task_id,
                            "state": state,
                            "raw_response": task_status
                        }
                    
                    # Unexpected status code
                    raise HTTPException(
                        status_code=status_response.status_code,
                        detail=f"SAM Gateway error: {status_response.text}"
                    )
                
                # Timeout - task still running after max polls
                raise HTTPException(
                    status_code=504,
                    detail=f"Task {task_id} did not complete within {max_polls * poll_interval} seconds. Task may still be processing."
                )
            else:
                # Unexpected response
                raise HTTPException(
                    status_code=submit_response.status_code,
                    detail=f"SAM Gateway error: {submit_response.text}"
                )
            
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Cannot connect to SAM REST Gateway. Make sure SAM is running on port 8080."
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
