"""
Meeting Agent - Analyzes Google Docs Meeting Minutes
Subscribes to squire/analysis/start, reads Google Docs, analyzes and summarizes
Publishes to squire/analysis/meeting/done
"""
import logging
import time
import asyncio
import httpx
import re
from typing import Dict, Any, List, Optional
from app.messaging.solace_client import get_solace_client
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Hardcoded Google Docs URLs (comma-separated or list)
GOOGLE_DOCS_URLS = settings.GOOGLE_DOCS_URLS.split(",") if settings.GOOGLE_DOCS_URLS else []


class GoogleDocsReader:
    """Helper class to read and analyze Google Docs"""
    
    @staticmethod
    def extract_doc_id(doc_url: str) -> Optional[str]:
        """Extract document ID from Google Docs URL"""
        # Pattern: /document/d/DOC_ID/
        match = re.search(r'/document/d/([a-zA-Z0-9-_]+)', doc_url)
        return match.group(1) if match else None
    
    async def read_doc_export(self, doc_url: str, format: str = "txt") -> str:
        """
        Read Google Doc by exporting it as plain text
        Works for public Google Docs or shared documents
        """
        doc_id = self.extract_doc_id(doc_url)
        if not doc_id:
            raise ValueError(f"Could not extract doc ID from URL: {doc_url}")
        
        # Google Docs export URL (public export)
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format={format}"
        
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            response = await client.get(export_url)
            response.raise_for_status()
            return response.text


def analyze_meeting_minutes(content: str) -> Dict[str, Any]:
    """Analyze meeting minutes and extract key information"""
    lines = [line.strip() for line in content.split('\n') if line.strip()]
    
    # Extract sections
    action_items = []
    decisions = []
    attendees = []
    topics = []
    
    content_lower = content.lower()
    
    # Look for action items (various patterns)
    action_patterns = [
        r'action\s*item[s]?[:\-]?\s*(.+?)(?:\n|$)',
        r'action[s]?[:\-]?\s*(.+?)(?:\n|$)',
        r'todo[s]?[:\-]?\s*(.+?)(?:\n|$)',
        r'next\s+step[s]?[:\-]?\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in action_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            item = match.group(1).strip()
            if item and len(item) > 3:
                action_items.append(item)
    
    # Look for decisions
    decision_patterns = [
        r'decision[s]?[:\-]?\s*(.+?)(?:\n|$)',
        r'decided[:\-]?\s*(.+?)(?:\n|$)',
        r'agreed[:\-]?\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in decision_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            decision = match.group(1).strip()
            if decision and len(decision) > 3:
                decisions.append(decision)
    
    # Look for attendees
    attendee_patterns = [
        r'attendee[s]?[:\-]?\s*(.+?)(?:\n|$)',
        r'participant[s]?[:\-]?\s*(.+?)(?:\n|$)',
        r'present[:\-]?\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in attendee_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            attendee_list = match.group(1).strip()
            if attendee_list:
                attendees.extend([a.strip() for a in re.split(r'[,;]', attendee_list) if a.strip()])
    
    # Extract key topics (simple keyword matching)
    key_phrases = [
        'project', 'deadline', 'budget', 'team', 'review', 'next steps',
        'discussion', 'proposal', 'feedback', 'update', 'status', 'milestone'
    ]
    for phrase in key_phrases:
        if phrase.lower() in content_lower:
            topics.append(phrase)
    
    # Create paragraph summary
    summary_parts = []
    
    summary_parts.append(f"This meeting document contains {len(lines)} lines of notes and covers several important topics.")
    
    if topics:
        topics_list = ', '.join(topics[:5])
        summary_parts.append(f"Key topics discussed include {topics_list}.")
    
    if attendees:
        attendees_list = ', '.join(attendees[:5])
        summary_parts.append(f"The meeting included {attendees_list} and other participants.")
    
    if decisions:
        summary_parts.append(f"The team made {len(decisions)} key decision{'s' if len(decisions) != 1 else ''}, including: {decisions[0][:150]}.")
    
    if action_items:
        summary_parts.append(f"Moving forward, {len(action_items)} action item{'s' if len(action_items) != 1 else ''} {'were' if len(action_items) > 1 else 'was'} identified for follow-up.")
    
    if not action_items and not decisions:
        summary_parts.append("The meeting focused on discussion and status updates.")
    
    summary_paragraph = " ".join(summary_parts)
    
    # Create detailed breakdown for reference
    details = f"\n\nDetailed Breakdown:\n"
    details += f"Document Length: {len(content)} characters, {len(lines)} lines\n"
    if topics:
        details += f"Key Topics: {', '.join(topics[:5])}\n"
    if action_items:
        details += f"\nAction Items ({len(action_items)}):\n"
        for i, item in enumerate(action_items[:10], 1):
            details += f"  {i}. {item[:100]}{'...' if len(item) > 100 else ''}\n"
    if decisions:
        details += f"\nDecisions ({len(decisions)}):\n"
        for i, decision in enumerate(decisions[:10], 1):
            details += f"  {i}. {decision[:100]}{'...' if len(decision) > 100 else ''}\n"
    if attendees:
        details += f"\nAttendees: {', '.join(attendees[:10])}\n"
    
    summary = summary_paragraph + details
    
    # Create review assessment
    review = {
        "completeness": "high" if (action_items and decisions) else "medium" if action_items or decisions else "low",
        "action_items_count": len(action_items),
        "decisions_count": len(decisions),
        "attendees_count": len(attendees),
        "recommendations": []
    }
    
    if not action_items:
        review["recommendations"].append("No action items identified - consider documenting next steps")
    if not decisions:
        review["recommendations"].append("No decisions identified - consider documenting key decisions")
    if len(lines) < 50:
        review["recommendations"].append("Meeting notes seem brief - ensure all important points are captured")
    if not review["recommendations"]:
        review["recommendations"].append("Meeting notes are well-structured")
    
    return {
        "content_length": len(content),
        "line_count": len(lines),
        "action_items": action_items[:10],
        "decisions": decisions[:10],
        "attendees": attendees[:10],
        "topics": topics[:10],
        "summary": summary,
        "summary_paragraph": summary_paragraph,  # Clean paragraph for display
        "review": review
    }


async def handle_analysis_start(payload: dict):
    """Handle analysis start event - read and analyze Google Docs"""
    # Get doc URLs from payload or use hardcoded ones
    doc_urls = payload.get("meeting_docs", GOOGLE_DOCS_URLS)
    
    if not doc_urls:
        logger.warning("No Google Docs URLs provided or configured")
        client = get_solace_client()
        client.publish("squire/analysis/meeting/done", {
            "agent": "meeting",
            "status": "error",
            "error": "No Google Docs URLs provided",
            "analyses": []
        })
        return
    
    # Convert single string to list if needed
    if isinstance(doc_urls, str):
        doc_urls = [url.strip() for url in doc_urls.split(",")]
    
    logger.info(f"Meeting Agent: Analyzing {len(doc_urls)} meeting document(s)")
    
    try:
        reader = GoogleDocsReader()
        all_analyses = []
        
        for doc_url in doc_urls:
            doc_url = doc_url.strip()
            if not doc_url:
                continue
                
            try:
                logger.info(f"Reading Google Doc: {doc_url}")
                # Read doc content
                content = await reader.read_doc_export(doc_url, format="txt")
                
                # Analyze content
                analysis = analyze_meeting_minutes(content)
                analysis["doc_url"] = doc_url
                analysis["status"] = "completed"
                all_analyses.append(analysis)
                
                logger.info(f"Analyzed doc: {doc_url} - {analysis['review']['action_items_count']} action items, {analysis['review']['decisions_count']} decisions")
                
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error reading doc {doc_url}: {e.response.status_code}")
                all_analyses.append({
                    "doc_url": doc_url,
                    "status": "error",
                    "error": f"HTTP {e.response.status_code}: Document may not be publicly accessible"
                })
            except Exception as e:
                logger.error(f"Error reading doc {doc_url}: {e}", exc_info=True)
                all_analyses.append({
                    "doc_url": doc_url,
                    "status": "error",
                    "error": str(e)
                })
        
        if not all_analyses:
            raise ValueError("No documents were successfully analyzed")
        
        # Publish results
        client = get_solace_client()
        client.publish("squire/analysis/meeting/done", {
            "agent": "meeting",
            "status": "completed",
            "documents_analyzed": len(all_analyses),
            "analyses": all_analyses,
            "summary": f"Analyzed {len(all_analyses)} meeting document(s)"
        })
        
        logger.info(f"Meeting Agent: Completed analysis of {len(all_analyses)} document(s)")
        print(f"\n{'='*60}")
        print("MEETING AGENT - ANALYSIS COMPLETE")
        print(f"{'='*60}")
        for analysis in all_analyses:
            if analysis.get("status") == "completed":
                print(f"\nDocument: {analysis.get('doc_url', 'N/A')}")
                print(f"Action Items: {analysis['review']['action_items_count']}, Decisions: {analysis['review']['decisions_count']}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        logger.error(f"Error in meeting analysis: {e}", exc_info=True)
        client = get_solace_client()
        client.publish("squire/analysis/meeting/done", {
            "agent": "meeting",
            "status": "error",
            "error": str(e),
            "analyses": []
        })


def sync_handler(payload: dict):
    """Synchronous wrapper for async handler"""
    asyncio.run(handle_analysis_start(payload))


def main():
    """Main function to run Meeting Agent"""
    logger.info("Starting Meeting Agent...")
    if GOOGLE_DOCS_URLS:
        logger.info(f"Configuration: {len(GOOGLE_DOCS_URLS)} Google Doc(s) configured")
    else:
        logger.warning("No Google Docs URLs configured - agent will wait for URLs in payload")
    
    client = get_solace_client()
    client.subscribe("squire/analysis/start", sync_handler)
    logger.info("Meeting Agent subscribed to squire/analysis/start")
    
    try:
        logger.info("Meeting Agent is running. Waiting for events...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Meeting Agent shutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()

