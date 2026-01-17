"""
Manager Agent - Final Synthesis Agent
Receives combined PR and Meeting analyses from Join Agent
Creates comprehensive report and recommendations
Subscribes to squire/analysis/join and publishes final report
"""
import logging
import time
from app.messaging.solace_client import get_solace_client
from app.services.report_storage import store_report

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def synthesize_report(pr_analysis: dict, meeting_analysis: dict) -> dict:
    """Synthesize PR and Meeting analyses into comprehensive report"""
    
    # Extract key data
    pr_results = pr_analysis.get("analyses", [])
    meeting_results = meeting_analysis.get("analyses", [])
    
    # Build executive summary
    report = {
        "executive_summary": "",
        "pr_insights": {
            "total_prs": len(pr_results),
            "total_files_changed": sum(a.get("metrics", {}).get("files_changed", 0) for a in pr_results),
            "total_additions": sum(a.get("metrics", {}).get("additions", 0) for a in pr_results),
            "total_deletions": sum(a.get("metrics", {}).get("deletions", 0) for a in pr_results),
            "high_complexity_count": sum(1 for a in pr_results if a.get("review", {}).get("complexity") == "high"),
            "high_risk_count": sum(1 for a in pr_results if a.get("review", {}).get("risk_level") == "high"),
        },
        "meeting_insights": {
            "documents_analyzed": len(meeting_results),
            "total_action_items": sum(
                len(a.get("action_items", [])) for a in meeting_results if a.get("status") == "completed"
            ),
            "total_decisions": sum(
                len(a.get("decisions", [])) for a in meeting_results if a.get("status") == "completed"
            ),
            "total_attendees": sum(
                len(a.get("attendees", [])) for a in meeting_results if a.get("status") == "completed"
            ),
        },
        "recommendations": [],
        "action_items": [],
        "detailed_pr_summaries": [],
        "detailed_meeting_summaries": []
    }
    
    # PR Summary
    if pr_results:
        report["detailed_pr_summaries"] = [
            {
                "pr_number": a.get("pr_number"),
                "title": a.get("title"),
                "url": a.get("url"),
                "summary": a.get("summary", "")[:300],
                "complexity": a.get("review", {}).get("complexity"),
                "risk_level": a.get("review", {}).get("risk_level"),
                "metrics": a.get("metrics", {})
            }
            for a in pr_results
        ]
    
    # Meeting Summary
    if meeting_results:
        report["detailed_meeting_summaries"] = [
            {
                "doc_url": a.get("doc_url"),
                "action_items": a.get("action_items", []),
                "decisions": a.get("decisions", []),
                "attendees": a.get("attendees", []),
                "summary": a.get("summary", "")[:300]
            }
            for a in meeting_results if a.get("status") == "completed"
        ]
        
        # Collect all action items
        for analysis in meeting_results:
            if analysis.get("status") == "completed":
                report["action_items"].extend(analysis.get("action_items", []))
    
    # Generate recommendations
    pr_insights = report["pr_insights"]
    meeting_insights = report["meeting_insights"]
    
    if pr_insights["high_complexity_count"] > 0:
        report["recommendations"].append(
            f"High complexity PRs detected ({pr_insights['high_complexity_count']}) - ensure adequate code review time"
        )
    
    if pr_insights["high_risk_count"] > 0:
        report["recommendations"].append(
            f"High risk PRs detected ({pr_insights['high_risk_count']}) - prioritize thorough testing"
        )
    
    if meeting_insights["total_action_items"] > 0:
        report["recommendations"].append(
            f"Meeting identified {meeting_insights['total_action_items']} action items - ensure follow-up and assignment"
        )
    
    if pr_insights["total_prs"] > 0 and meeting_insights["total_action_items"] > 0:
        report["recommendations"].append(
            "PR activity and meeting action items are aligned - continue coordinated development efforts"
        )
    
    if not report["recommendations"]:
        report["recommendations"].append("All systems operational - no immediate concerns identified")
    
    # Executive Summary
    report["executive_summary"] = f"""
EXECUTIVE SUMMARY
=================

Code Review Status:
- PRs Analyzed: {pr_insights['total_prs']}
- Files Changed: {pr_insights['total_files_changed']}
- Net Code Changes: +{pr_insights['total_additions']} / -{pr_insights['total_deletions']} lines
- High Complexity PRs: {pr_insights['high_complexity_count']}
- High Risk PRs: {pr_insights['high_risk_count']}

Meeting Activity Status:
- Documents Analyzed: {meeting_insights['documents_analyzed']}
- Action Items Identified: {meeting_insights['total_action_items']}
- Decisions Documented: {meeting_insights['total_decisions']}
- Attendees Tracked: {meeting_insights['total_attendees']}

Key Recommendations:
{chr(10).join(f"- {rec}" for rec in report['recommendations'])}

Next Steps:
- Review PR summaries for critical changes requiring attention
- Follow up on meeting action items to ensure completion
- Monitor high-risk PRs through deployment process
"""
    
    return report


def handle_join_event(payload: dict):
    """Handle join event - synthesize PR and Meeting analyses into final report"""
    logger.info("Manager Agent received join event with both analyses")
    
    try:
        pr_analysis = payload.get("pr_analysis", {})
        meeting_analysis = payload.get("meeting_analysis", {})
        
        # Validate data
        if not pr_analysis or pr_analysis.get("status") != "completed":
            logger.warning("PR analysis missing or incomplete")
        
        if not meeting_analysis or meeting_analysis.get("status") != "completed":
            logger.warning("Meeting analysis missing or incomplete")
        
        # Synthesize report
        report = synthesize_report(pr_analysis, meeting_analysis)
        
        # Store report in storage (accessible via API)
        full_report = {
            "agent": "manager",
            "status": "completed",
            "report": report,
            "pr_analysis": pr_analysis,
            "meeting_analysis": meeting_analysis
        }
        store_report(full_report)
        
        # Publish final report
        client = get_solace_client()
        client.publish("squire/manager/report", {
            "agent": "manager",
            "status": "completed",
            "report": report,
            "timestamp": None
        })
        
        logger.info("Manager Agent published final report to squire/manager/report and stored for API access")
        
        print(f"\n{'='*60}")
        print("MANAGER AGENT - FINAL REPORT GENERATED")
        print(f"{'='*60}")
        print(report["executive_summary"])
        print(f"{'='*60}\n")
        
    except Exception as e:
        logger.error(f"Error synthesizing report: {e}", exc_info=True)
        client = get_solace_client()
        client.publish("squire/manager/report", {
            "agent": "manager",
            "status": "error",
            "error": str(e)
        })


def main():
    """Main function to run Manager Agent"""
    logger.info("Starting Manager Agent...")
    
    client = get_solace_client()
    client.subscribe("squire/analysis/join", handle_join_event)
    logger.info("Manager Agent subscribed to squire/analysis/join")
    
    try:
        logger.info("Manager Agent is running. Waiting for combined analyses...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Manager Agent shutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()

