"""
Analysis API Endpoint
Triggers the analysis workflow: PR Agent + Meeting Agent → Join → Manager Agent
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.messaging.solace_client import get_solace_client
from app.services.report_storage import get_latest_report
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["analysis"])


class AnalysisRequest(BaseModel):
    """Request model for starting analysis workflow"""
    pr_count: Optional[int] = None  # Not used - always analyzes most recent merged PR
    meeting_docs: Optional[List[str]] = None  # Optional: override Google Docs URLs


class AnalysisResponse(BaseModel):
    """Response model for analysis workflow"""
    status: str
    message: str


@router.post("/analysis/start", response_model=AnalysisResponse)
async def start_analysis(request: AnalysisRequest = None):
    """
    Start the analysis workflow by publishing to squire/analysis/start topic
    
    This triggers:
    1. PR Agent - Analyzes the most recent merged PR from the hardcoded repo
    2. Meeting Agent - Analyzes Google Docs (hardcoded URLs)
    3. Join Agent - Waits for both to complete
    4. Manager Agent - Synthesizes final report
    """
    try:
        if request is None:
            request = AnalysisRequest()
        
        client = get_solace_client()
        
        # Build payload
        # Note: PR Agent now always analyzes the most recent merged PR (pr_count is ignored)
        payload = {
            "event": "start",
        }
        
        # Add meeting docs if provided
        if request.meeting_docs:
            payload["meeting_docs"] = request.meeting_docs
        
        success = client.publish("squire/analysis/start", payload)
        
        if success:
            logger.info("Analysis workflow started: published to squire/analysis/start")
            return AnalysisResponse(
                status="success",
                message="Analysis workflow started. PR Agent and Meeting Agent are analyzing in parallel."
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to publish analysis start event"
            )
            
    except Exception as e:
        logger.error(f"Error starting analysis workflow: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error starting analysis workflow: {str(e)}"
        )


@router.get("/analysis/report")
async def get_report():
    """
    Get the latest Manager Agent report
    
    Returns the most recent analysis report combining PR and Meeting analyses.
    The report is generated after both PR Agent and Meeting Agent complete their work.
    """
    report_data = get_latest_report()
    
    if report_data is None:
        raise HTTPException(
            status_code=404,
            detail="No report available yet. Please trigger an analysis first via POST /api/analysis/start"
        )
    
    return report_data

