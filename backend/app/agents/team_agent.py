"""
Team Agent - Analyzes Team Review feedback from database
Subscribes to squire/analysis/start, queries TeamReview table, analyzes and summarizes
Publishes to squire/analysis/team/done
"""
import logging
import time
import re
from typing import Dict, Any, Optional
from app.messaging.solace_client import get_solace_client
from app.db.database import SessionLocal, init_db
from app.models.team_review import TeamReview

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def analyze_team_review(text: str) -> Dict[str, Any]:
    """Analyze team review text and extract detailed insights"""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    text_lower = text.lower()
    
    # Extract key information
    sentiment_keywords = {
        "positive": ["great", "excellent", "good", "well", "improved", "success", "happy", "satisfied", "pleased", "solid", "impressive", "outstanding"],
        "negative": ["issue", "problem", "concern", "difficult", "challenge", "struggle", "frustrated", "worried", "error", "bug", "broken"],
        "neutral": ["update", "status", "progress", "note", "information", "reviewed", "checked"]
    }
    
    sentiment_scores = {key: 0 for key in sentiment_keywords}
    for sentiment, keywords in sentiment_keywords.items():
        for keyword in keywords:
            sentiment_scores[sentiment] += text_lower.count(keyword)
    
    # Determine overall sentiment
    if sentiment_scores["positive"] > sentiment_scores["negative"]:
        overall_sentiment = "positive"
    elif sentiment_scores["negative"] > sentiment_scores["positive"]:
        overall_sentiment = "negative"
    else:
        overall_sentiment = "neutral"
    
    # Extract specific technical details
    pr_numbers = re.findall(r'PR\s*#?\s*(\d+)', text, re.IGNORECASE)
    ticket_numbers = re.findall(r'(?:ticket|issue|task)\s*#?\s*(\d+)', text, re.IGNORECASE)
    
    # Extract technologies/tools mentioned
    technologies = []
    tech_keywords = [
        "JWT", "Redis", "Docker", "Kubernetes", "React", "Python", "JavaScript", "TypeScript",
        "FastAPI", "Django", "Flask", "PostgreSQL", "MongoDB", "Git", "GitHub", "CI/CD",
        "API", "REST", "GraphQL", "AWS", "Azure", "GCP", "Kubernetes", "Docker", "Jenkins",
        "unit test", "integration test", "pytest", "jest", "SQL", "NoSQL", "authentication",
        "authorization", "rate limiting", "caching", "microservices", "lambda", "serverless"
    ]
    for tech in tech_keywords:
        if tech.lower() in text_lower:
            technologies.append(tech)
    
    # Extract code quality aspects
    quality_aspects = []
    quality_keywords = {
        "error handling": ["error handling", "exception", "try/catch", "error management"],
        "testing": ["test", "unit test", "integration test", "coverage", "pytest", "jest"],
        "documentation": ["documentation", "doc", "README", "API doc", "comment"],
        "code quality": ["refactor", "clean code", "best practice", "code review", "type hint"],
        "performance": ["performance", "optimization", "speed", "efficiency", "latency"],
        "security": ["security", "vulnerability", "encryption", "authentication", "authorization"]
    }
    for aspect, keywords in quality_keywords.items():
        if any(kw in text_lower for kw in keywords):
            quality_aspects.append(aspect)
    
    # Extract specific strengths
    strengths = []
    strength_patterns = [
        r'(?:solid|good|excellent|great|impressive|well done|strong)\s+([^.]+?)(?:\.|$)',
        r'(?:properly|correctly|effectively)\s+([^.]+?)(?:\.|$)',
        r'(?:clean|clear|comprehensive|thorough)\s+([^.]+?)(?:\.|$)',
    ]
    for pattern in strength_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            strength = match.group(1).strip()[:100]
            if strength and len(strength) > 10:
                strengths.append(strength)
    
    # Extract specific concerns/improvements
    concerns = []
    concern_patterns = [
        r'(?:concern|issue|problem|forgot|missed|missing|needs?\s+(?:to\s+)?(?:be|improve|fix))\s+([^.]+?)(?:\.|$)',
        r'(?:could\s+(?:be|use)|should\s+(?:be|use)|would\s+(?:be|benefit))\s+([^.]+?)(?:\.|$)',
    ]
    for pattern in concern_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            concern = match.group(1).strip()[:100]
            if concern and len(concern) > 10:
                concerns.append(concern)
    
    # Extract topics/themes
    topics = []
    common_topics = [
        "collaboration", "communication", "deadline", "quality", "process",
        "teamwork", "feedback", "improvement", "blocker", "achievement",
        "code review", "PR review", "technical review", "architecture", "implementation"
    ]
    for topic in common_topics:
        if topic in text_lower:
            topics.append(topic)
    
    # Extract action items/recommendations
    action_items = []
    action_patterns = [
        r'(?:should|needs?\s+to|must)\s+([^.]+?)(?:\.|$)',
        r'(?:recommend|suggest|consider)\s+([^.]+?)(?:\.|$)',
    ]
    for pattern in action_patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            action = match.group(1).strip()[:100]
            if action and len(action) > 10:
                action_items.append(action)
    
    # Create detailed, specific summary paragraph
    summary_parts = []
    
    # Opening with context
    if pr_numbers:
        summary_parts.append(f"This team review focuses on PR #{pr_numbers[0]} and provides comprehensive technical feedback.")
    else:
        summary_parts.append(f"This team review provides detailed technical feedback on code and implementation work.")
    
    # Sentiment with specifics
    if overall_sentiment == "positive":
        summary_parts.append("The review maintains a positive and constructive tone throughout, highlighting both strengths and areas for improvement.")
    elif overall_sentiment == "negative":
        summary_parts.append("The review identifies several concerns that require attention, while maintaining a constructive approach to addressing issues.")
    else:
        summary_parts.append("The review provides a balanced, objective assessment of the work completed.")
    
    # Technical details
    if technologies:
        tech_list = ', '.join(list(set(technologies))[:5])
        summary_parts.append(f"Technical implementation involves {tech_list}, demonstrating engagement with modern development practices.")
    
    if quality_aspects:
        aspects_list = ', '.join(quality_aspects[:3])
        summary_parts.append(f"The review specifically addresses {aspects_list}, indicating a thorough code quality assessment.")
    
    # Specific strengths
    if strengths:
        if len(strengths) == 1:
            summary_parts.append(f"A notable strength identified is: {strengths[0]}.")
        else:
            strengths_text = '; '.join([s[:80] for s in strengths[:2]])
            summary_parts.append(f"Key strengths highlighted include: {strengths_text}.")
    
    # Specific concerns/improvements
    if concerns:
        if len(concerns) == 1:
            summary_parts.append(f"The review notes a specific area for improvement: {concerns[0]}.")
        else:
            concerns_text = '; '.join([c[:80] for c in concerns[:2]])
            summary_parts.append(f"Areas requiring attention include: {concerns_text}.")
    
    # Action items
    if action_items:
        summary_parts.append(f"The reviewer provides {len(action_items)} specific recommendation{'s' if len(action_items) != 1 else ''} for enhancing the implementation.")
    
    summary_paragraph = " ".join(summary_parts)
    
    # Extract key points (meaningful sentences)
    sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
    key_points = [s for s in sentences if len(s) > 50][:3] if sentences else []
    
    return {
        "text_length": len(text),
        "line_count": len(lines),
        "sentiment": overall_sentiment,
        "sentiment_scores": sentiment_scores,
        "topics": topics,
        "pr_numbers": pr_numbers,
        "ticket_numbers": ticket_numbers,
        "technologies": list(set(technologies)),
        "quality_aspects": quality_aspects,
        "strengths": strengths[:5],
        "concerns": concerns[:5],
        "action_items": action_items[:5],
        "key_points": key_points,
        "summary": summary_paragraph,
        "summary_paragraph": summary_paragraph,
        "review": {
            "sentiment": overall_sentiment,
            "topics_identified": len(topics),
            "key_points_count": len(key_points),
            "technologies_mentioned": len(technologies),
            "strengths_count": len(strengths),
            "concerns_count": len(concerns)
        }
    }


def handle_analysis_start(payload: dict):
    """Handle analysis start event - query most recent TeamReview and analyze"""
    logger.info("Team Agent: Starting analysis of most recent team review")
    
    try:
        # Initialize database if needed
        init_db()
        
        # Get database session
        db = SessionLocal()
        
        try:
            # Query most recent TeamReview entry
            most_recent = db.query(TeamReview).order_by(TeamReview.created_at.desc()).first()
            
            if not most_recent:
                logger.warning("No team reviews found in database")
                client = get_solace_client()
                client.publish("squire/analysis/team/done", {
                    "agent": "team",
                    "status": "completed",
                    "message": "No team reviews found in database",
                    "analyses": []
                })
                return
            
            logger.info(f"Found team review #{most_recent.id} from {most_recent.team_member or 'Unknown'}")
            
            # Analyze the review text
            analysis = analyze_team_review(most_recent.text)
            analysis["review_id"] = most_recent.id
            analysis["team_member"] = most_recent.team_member
            analysis["created_at"] = most_recent.created_at.isoformat() if most_recent.created_at else None
            analysis["status"] = "completed"
            
            # Publish results
            client = get_solace_client()
            client.publish("squire/analysis/team/done", {
                "agent": "team",
                "status": "completed",
                "analyses": [analysis],
                "count": 1,
                "summary": f"Analyzed team review #{most_recent.id} from {most_recent.team_member or 'Unknown'}"
            })
            
            logger.info(f"Team Agent: Completed analysis of review #{most_recent.id}")
            print(f"\n{'='*60}")
            print("TEAM AGENT - ANALYSIS COMPLETE")
            print(f"{'='*60}")
            print(f"Review ID: {most_recent.id}")
            print(f"Team Member: {most_recent.team_member or 'Unknown'}")
            print(f"Sentiment: {analysis['sentiment']}")
            print(f"Topics: {', '.join(analysis['topics'][:5]) if analysis['topics'] else 'N/A'}")
            print(f"{'='*60}\n")
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error analyzing team review: {e}", exc_info=True)
        client = get_solace_client()
        client.publish("squire/analysis/team/done", {
            "agent": "team",
            "status": "error",
            "error": str(e),
            "analyses": []
        })


def sync_handler(payload: dict):
    """Synchronous wrapper for handler"""
    handle_analysis_start(payload)


def main():
    """Main function to run Team Agent"""
    logger.info("Starting Team Agent...")
    
    client = get_solace_client()
    client.subscribe("squire/analysis/start", sync_handler)
    logger.info("Team Agent subscribed to squire/analysis/start")
    
    try:
        logger.info("Team Agent is running. Waiting for events...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Team Agent shutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()

