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
    
    # Analyze what the team actually did in the meeting
    activities = []
    accomplishments = []
    
    # Look for what was accomplished/completed
    accomplishment_patterns = [
        r'completed[:\-]?\s*(.+?)(?:\n|$)',
        r'finished[:\-]?\s*(.+?)(?:\n|$)',
        r'accomplished[:\-]?\s*(.+?)(?:\n|$)',
        r'delivered[:\-]?\s*(.+?)(?:\n|$)',
        r'solved[:\-]?\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in accomplishment_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            accomplishment = match.group(1).strip()
            if accomplishment and len(accomplishment) > 3:
                accomplishments.append(accomplishment)
    
    # Look for activities/work done
    activity_patterns = [
        r'discussed[:\-]?\s*(.+?)(?:\n|$)',
        r'reviewed[:\-]?\s*(.+?)(?:\n|$)',
        r'presented[:\-]?\s*(.+?)(?:\n|$)',
        r'demonstrated[:\-]?\s*(.+?)(?:\n|$)',
        r'worked on[:\-]?\s*(.+?)(?:\n|$)',
    ]
    
    for pattern in activity_patterns:
        matches = re.finditer(pattern, content_lower, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            activity = match.group(1).strip()
            if activity and len(activity) > 3:
                activities.append(activity)
    
    # Extract more specific details
    # Extract project/module names
    projects = re.findall(r'(?:project|module|feature|component)\s+(?:called\s+)?["\']?([A-Z][a-zA-Z0-9\s]+)["\']?', content, re.IGNORECASE)
    
    # Extract deadlines/timelines
    deadlines = re.findall(r'(?:deadline|due\s+date|by|target|ETA|timeline)[:\-]?\s*([^.]+?)(?:\.|$)', content, re.IGNORECASE)
    
    # Extract specific problems/issues
    problems = []
    problem_patterns = [
        r'(?:problem|issue|blocker|challenge|difficulty)\s+(?:is|with|that)\s+([^.]+?)(?:\.|$)',
        r'(?:facing|encountering|experiencing)\s+([^.]+?)(?:\.|$)',
    ]
    for pattern in problem_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            problem = match.group(1).strip()[:150]
            if problem and len(problem) > 10:
                problems.append(problem)
    
    # Extract solutions/approaches
    solutions = []
    solution_patterns = [
        r'(?:solution|approach|fix|resolve|address)\s+(?:is|was|will be|to)\s+([^.]+?)(?:\.|$)',
        r'(?:decided\s+to|agreed\s+to|plan\s+to)\s+([^.]+?)(?:\.|$)',
    ]
    for pattern in solution_patterns:
        matches = re.finditer(pattern, content, re.IGNORECASE)
        for match in matches:
            solution = match.group(1).strip()[:150]
            if solution and len(solution) > 10:
                solutions.append(solution)
    
    # Extract metrics/numbers
    metrics = re.findall(r'(\d+\s*(?:percent|%|hours|days|weeks|people|members|items|tasks|PRs|issues))', content, re.IGNORECASE)
    
    # Create comprehensive, detailed paragraph summary
    summary_parts = []
    
    # Opening with context and scope
    summary_parts.append(f"This meeting document contains {len(lines)} lines of detailed notes covering comprehensive team discussion and decision-making.")
    
    if attendees:
        attendees_list = ', '.join(attendees[:4])
        summary_parts.append(f"The meeting involved {attendees_list}{' and others' if len(attendees) > 4 else ''}, representing key stakeholders and team members.")
    
    # Specific topics with context
    if topics:
        topics_list = ', '.join(topics[:5])
        summary_parts.append(f"Discussion centered on {topics_list}, indicating a focused agenda addressing multiple aspects of project development.")
    
    # Project/module specifics
    if projects:
        projects_list = ', '.join(projects[:3])
        summary_parts.append(f"Specific focus was given to {projects_list}, demonstrating targeted attention to key deliverables.")
    
    # Accomplishments with details
    if accomplishments:
        if len(accomplishments) == 1:
            summary_parts.append(f"A significant accomplishment was achieved during the meeting: {accomplishments[0][:250]}.")
        else:
            accomplishments_text = '; '.join([a[:120] for a in accomplishments[:2]])
            summary_parts.append(f"The team documented several accomplishments including: {accomplishments_text}.")
    
    # Activities with specifics
    if activities:
        activities_text = '; '.join([a[:120] for a in activities[:2]])
        summary_parts.append(f"Detailed review and discussion occurred on: {activities_text}, ensuring thorough examination of key work items.")
    
    # Problems and solutions
    if problems:
        if len(problems) == 1:
            summary_parts.append(f"A specific problem was identified: {problems[0][:200]}.")
        elif solutions:
            summary_parts.append(f"Several challenges were discussed, including {problems[0][:150]}, with corresponding solutions being evaluated.")
    
    if solutions:
        solutions_text = '; '.join([s[:120] for s in solutions[:2]])
        summary_parts.append(f"The team agreed on solutions and approaches: {solutions_text}.")
    
    # Decisions with impact
    if decisions:
        if len(decisions) == 1:
            summary_parts.append(f"A critical decision was made: {decisions[0][:250]}, which will guide future development efforts.")
        else:
            summary_parts.append(f"The meeting resulted in {len(decisions)} key decisions, with the primary decision being: {decisions[0][:200]}, establishing direction for the team.")
    
    # Action items with specifics
    if action_items:
        if len(action_items) == 1:
            summary_parts.append(f"One concrete action item was established: {action_items[0][:250]}, ensuring clear next steps.")
        else:
            summary_parts.append(f"Moving forward, {len(action_items)} specific action items were defined, with priority given to: {action_items[0][:200]}, demonstrating a structured approach to follow-up.")
    
    # Metrics and deadlines
    if metrics:
        metrics_text = ', '.join(metrics[:3])
        summary_parts.append(f"Quantifiable metrics and timelines were established: {metrics_text}, providing measurable targets.")
    
    if deadlines:
        deadlines_text = '; '.join([d[:100] for d in deadlines[:2]])
        summary_parts.append(f"Specific timelines were discussed: {deadlines_text}, ensuring alignment on delivery expectations.")
    
    if not action_items and not decisions and not accomplishments:
        summary_parts.append("The meeting primarily focused on detailed discussion, status updates, and collaborative problem-solving.")
    
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
        "projects": projects[:5],
        "problems": problems[:5],
        "solutions": solutions[:5],
        "deadlines": deadlines[:5],
        "metrics": metrics[:5],
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

