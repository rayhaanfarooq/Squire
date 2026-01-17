"""
PR Agent - Analyzes GitHub Pull Requests
Subscribes to squire/analysis/start, fetches PRs from hardcoded repo, analyzes and summarizes
Publishes to squire/analysis/pr/done
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

# Hardcoded configuration
REPO_OWNER = settings.GITHUB_REPO_OWNER  # e.g., "facebook"
REPO_NAME = settings.GITHUB_REPO_NAME  # e.g., "react"
GITHUB_TOKEN = settings.GITHUB_TOKEN


class PRFetcher:
    """Helper class to fetch and analyze PR data from GitHub"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.token = github_token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Squire-PR-Agent"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"
    
    async def fetch_recent_prs(self, owner: str, repo: str, limit: int = 5, state: str = "closed") -> List[Dict[str, Any]]:
        """Fetch recent PRs from a repository (default: closed/merged PRs)"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
            # Sort by updated date, descending - most recently updated (merged) PRs first
            params = {"state": state, "per_page": limit, "sort": "updated", "direction": "desc"}
            
            response = await client.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            prs = response.json()
            
            # Filter to only merged PRs (have merged_at timestamp) and sort by merged_at
            merged_prs = [pr for pr in prs if pr.get("merged_at")]
            # Sort by merged_at descending (most recent merged first)
            merged_prs.sort(key=lambda x: x.get("merged_at", ""), reverse=True)
            
            return merged_prs[:limit]
    
    async def fetch_pr_details(self, owner: str, repo: str, pr_number: int) -> Dict[str, Any]:
        """Fetch detailed PR information including files and reviews"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Fetch PR details
            pr_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}",
                headers=self.headers
            )
            pr_response.raise_for_status()
            pr_data = pr_response.json()
            
            # Fetch PR files
            files_response = await client.get(
                f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files",
                headers=self.headers
            )
            files_response.raise_for_status()
            files_data = files_response.json()
            
            return {
                "pr": pr_data,
                "files": files_data
            }
    
    def analyze_pr(self, pr_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze PR and create summary with review"""
        pr = pr_data["pr"]
        files = pr_data.get("files", [])
        
        # Calculate metrics
        total_additions = pr.get("additions", 0)
        total_deletions = pr.get("deletions", 0)
        files_changed = len(files)
        
        # Analyze file types
        file_types = {}
        for f in files:
            filename = f.get("filename", "")
            ext = filename.split('.')[-1] if '.' in filename else "other"
            file_types[ext] = file_types.get(ext, 0) + 1
        
        # Extract key files (files with most changes)
        key_files = sorted(
            files,
            key=lambda x: x.get("additions", 0) + x.get("deletions", 0),
            reverse=True
        )[:5]
        
        # Create summary
        summary = f"PR #{pr.get('number')}: {pr.get('title')}\n"
        summary += f"Author: {pr.get('user', {}).get('login')}\n"
        summary += f"Status: {pr.get('state')}\n"
        summary += f"Created: {pr.get('created_at')}\n"
        summary += f"\nChanges:\n"
        summary += f"  - Files changed: {files_changed}\n"
        summary += f"  - Additions: +{total_additions}\n"
        summary += f"  - Deletions: -{total_deletions}\n"
        summary += f"  - Net change: {total_additions - total_deletions} lines\n"
        
        if file_types:
            summary += f"\nFile types: {', '.join(f'{k}({v})' for k, v in file_types.items())}\n"
        
        # Key files
        if key_files:
            summary += f"\nKey files modified:\n"
            for f in key_files:
                summary += f"  - {f.get('filename')} (+{f.get('additions', 0)}/-{f.get('deletions', 0)})\n"
        
        # PR description excerpt
        body = pr.get("body", "")
        if body:
            summary += f"\nDescription: {body[:300]}...\n"
        
        # Create review assessment
        review = {
            "complexity": "high" if total_additions + total_deletions > 500 else "medium" if total_additions + total_deletions > 100 else "low",
            "risk_level": "high" if files_changed > 20 else "medium" if files_changed > 5 else "low",
            "recommendations": []
        }
        
        if total_additions + total_deletions > 1000:
            review["recommendations"].append("Large PR - consider breaking into smaller changes")
        if files_changed > 15:
            review["recommendations"].append("Many files changed - ensure thorough testing")
        if not review["recommendations"]:
            review["recommendations"].append("PR looks manageable")
        
        return {
            "pr_number": pr.get("number"),
            "title": pr.get("title"),
            "author": pr.get("user", {}).get("login"),
            "url": pr.get("html_url"),
            "state": pr.get("state"),
            "created_at": pr.get("created_at"),
            "updated_at": pr.get("updated_at"),
            "metrics": {
                "files_changed": files_changed,
                "additions": total_additions,
                "deletions": total_deletions,
                "net_change": total_additions - total_deletions,
                "file_types": file_types
            },
            "summary": summary,
            "review": review
        }


async def handle_analysis_start(payload: dict):
    """Handle analysis start event - fetch and analyze the most recent merged PR"""
    logger.info(f"PR Agent: Starting analysis for {REPO_OWNER}/{REPO_NAME}")
    
    try:
        fetcher = PRFetcher(github_token=GITHUB_TOKEN if GITHUB_TOKEN else None)
        
        # Fetch the most recent merged PR (only 1)
        logger.info(f"Fetching most recent merged PR from {REPO_OWNER}/{REPO_NAME}")
        prs = await fetcher.fetch_recent_prs(REPO_OWNER, REPO_NAME, limit=1, state="closed")
        
        if not prs:
            logger.warning(f"No merged PRs found for {REPO_OWNER}/{REPO_NAME}")
            client = get_solace_client()
            client.publish("squire/analysis/pr/done", {
                "agent": "pr",
                "status": "completed",
                "repo": f"{REPO_OWNER}/{REPO_NAME}",
                "analyses": [],
                "count": 0,
                "message": f"No merged PRs found for {REPO_OWNER}/{REPO_NAME}"
            })
            return
        
        # Get the most recent merged PR (first in the list since we sort by updated desc)
        pr = prs[0]
        pr_number = pr.get("number")
        pr_title = pr.get("title")
        merged_at = pr.get("merged_at")
        
        # Only analyze if it's actually merged (has merged_at timestamp)
        if not merged_at:
            logger.warning(f"PR #{pr_number} is closed but not merged. Skipping.")
            client = get_solace_client()
            client.publish("squire/analysis/pr/done", {
                "agent": "pr",
                "status": "completed",
                "repo": f"{REPO_OWNER}/{REPO_NAME}",
                "analyses": [],
                "count": 0,
                "message": f"Most recent closed PR #{pr_number} is not merged yet"
            })
            return
        
        logger.info(f"Analyzing most recent merged PR #{pr_number}: {pr_title} (merged at {merged_at})")
        
        # Fetch detailed PR data and analyze
        pr_data = await fetcher.fetch_pr_details(REPO_OWNER, REPO_NAME, pr_number)
        analysis = fetcher.analyze_pr(pr_data)
        
        # Add merged timestamp to analysis
        analysis["merged_at"] = merged_at
        
        # Publish results (single PR analysis)
        client = get_solace_client()
        client.publish("squire/analysis/pr/done", {
            "agent": "pr",
            "status": "completed",
            "repo": f"{REPO_OWNER}/{REPO_NAME}",
            "analyses": [analysis],  # Single PR in array for consistency with Manager Agent
            "count": 1,
            "summary": f"Analyzed most recent merged PR #{pr_number} from {REPO_OWNER}/{REPO_NAME}"
        })
        
        logger.info(f"PR Agent: Completed analysis of merged PR #{pr_number}")
        print(f"\n{'='*60}")
        print("PR AGENT - ANALYSIS COMPLETE")
        print(f"{'='*60}")
        print(f"\nPR #{analysis['pr_number']}: {analysis['title']}")
        print(f"Merged at: {merged_at}")
        print(f"Complexity: {analysis['review']['complexity']}, Risk: {analysis['review']['risk_level']}")
        print(f"{'='*60}\n")
        
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching PRs: {e.response.status_code} - {e.response.text}")
        client = get_solace_client()
        client.publish("squire/analysis/pr/done", {
            "agent": "pr",
            "status": "error",
            "error": f"HTTP {e.response.status_code}: Failed to fetch PRs",
            "repo": f"{REPO_OWNER}/{REPO_NAME}"
        })
    except Exception as e:
        logger.error(f"Error analyzing PRs: {e}", exc_info=True)
        client = get_solace_client()
        client.publish("squire/analysis/pr/done", {
            "agent": "pr",
            "status": "error",
            "error": str(e),
            "repo": f"{REPO_OWNER}/{REPO_NAME}"
        })


def sync_handler(payload: dict):
    """Synchronous wrapper for async handler"""
    asyncio.run(handle_analysis_start(payload))


def main():
    """Main function to run PR Agent"""
    logger.info("Starting PR Agent...")
    logger.info(f"Configuration: {REPO_OWNER}/{REPO_NAME}")
    
    client = get_solace_client()
    client.subscribe("squire/analysis/start", sync_handler)
    logger.info("PR Agent subscribed to squire/analysis/start")
    
    try:
        logger.info("PR Agent is running. Waiting for events...")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("PR Agent shutting down...")
        client.disconnect()


if __name__ == "__main__":
    main()

