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
    
    def analyze_patches(self, files: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze actual patch/diff content to understand what features/changes were made"""
        features_detected = []
        change_patterns = []
        code_quality_notes = []
        files_with_patches = 0
        total_patch_lines = 0
        
        for file_info in files:
            patch = file_info.get("patch", "")
            if not patch:
                continue  # Binary files or very large files may not have patch
            
            files_with_patches += 1
            filename = file_info.get("filename", "")
            patch_lower = patch.lower()
            
            # Count actual changed lines in patch
            patch_lines = [line for line in patch.split('\n') 
                          if line.startswith('+') or line.startswith('-')]
            added_code_lines = [line for line in patch_lines 
                               if line.startswith('+') and not line.startswith('+++')]
            removed_code_lines = [line for line in patch_lines 
                                 if line.startswith('-') and not line.startswith('---')]
            total_patch_lines += len(added_code_lines) + len(removed_code_lines)
            
            # Detect common features and patterns
            # Async/await functionality
            if ("async def" in patch or "await " in patch) and "async" not in [f.lower() for f in features_detected]:
                features_detected.append("async/await functionality")
            
            # Testing additions
            if ("def test_" in patch or "pytest" in patch_lower or "unittest" in patch_lower) and "test" not in [f.lower() for f in features_detected]:
                features_detected.append("test additions")
            
            # New classes
            if "class " in patch and ("def __init__" in patch or "class " in added_code_lines):
                if "new classes" not in [f.lower() for f in features_detected]:
                    features_detected.append("new class definitions")
            
            # API endpoints (FastAPI, Flask, Django routes)
            if ("@app." in patch or "@router." in patch or "@api." in patch or 
                "def get_" in patch or "def post_" in patch or "def put_" in patch):
                if "API endpoints" not in features_detected:
                    features_detected.append("API endpoints")
            
            # Database/SQL changes
            if ("CREATE TABLE" in patch or "INSERT INTO" in patch or "ALTER TABLE" in patch or
                "db." in patch_lower or "sqlalchemy" in patch_lower):
                if "database changes" not in change_patterns:
                    change_patterns.append("database schema modifications")
            
            # Import statements (new dependencies)
            added_imports = [line for line in added_code_lines if line.startswith('+import ') or line.startswith('+from ')]
            if added_imports and "dependencies" not in [c.lower() for c in change_patterns]:
                change_patterns.append("dependency additions")
            
            # Error handling improvements
            if "try:" in patch and "except" in patch:
                if "error handling" not in [c.lower() for c in change_patterns]:
                    change_patterns.append("error handling improvements")
            
            # Refactoring (many deletions and additions in same areas)
            additions = file_info.get("additions", 0)
            deletions = file_info.get("deletions", 0)
            if additions > 10 and deletions > 10:
                if "refactoring" not in [c.lower() for c in change_patterns]:
                    change_patterns.append("code refactoring")
            
            # Function modifications
            added_functions = [line for line in added_code_lines if line.startswith('+def ') or line.startswith('+    def ')]
            removed_functions = [line for line in removed_code_lines if line.startswith('-def ') or line.startswith('-    def ')]
            if (added_functions or removed_functions) and "function modifications" not in [c.lower() for c in change_patterns]:
                change_patterns.append("function modifications")
            
            # Type hints (Python)
            if ":" in patch and "->" in patch and "type hints" not in [c.lower() for c in change_patterns]:
                change_patterns.append("type hint additions")
            
            # Configuration changes
            if ("config" in filename.lower() or "settings" in filename.lower() or 
                "ENV" in patch or "environment" in patch_lower):
                if "configuration" not in [c.lower() for c in change_patterns]:
                    change_patterns.append("configuration changes")
            
            # Code quality issues
            if "TODO" in patch or "FIXME" in patch:
                code_quality_notes.append(f"TODOs/FIXMEs found in {filename}")
            
            if "print(" in added_code_lines and "logging" not in patch_lower:
                code_quality_notes.append(f"Potential debug print statements in {filename}")
        
        return {
            "features_detected": features_detected,
            "change_patterns": change_patterns,
            "code_quality_notes": code_quality_notes,
            "files_with_patches": files_with_patches,
            "total_patch_lines_analyzed": total_patch_lines
        }

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
        
        # Analyze actual patch/diff content to understand code changes
        patch_analysis = self.analyze_patches(files)
        
        # Create comprehensive paragraph summary
        body = pr.get("body", "") or ""
        author = pr.get('user', {}).get('login', 'Unknown')
        pr_number = pr.get('number')
        pr_title = pr.get('title', 'Untitled')
        
        # Build paragraph summary
        summary_parts = []
        summary_parts.append(f"This pull request (#{pr_number}) by {author} introduces significant changes to the codebase.")
        summary_parts.append(f"The PR, titled '{pr_title}', modifies {files_changed} file{'s' if files_changed != 1 else ''} with {total_additions} additions and {total_deletions} deletions, resulting in a net change of {total_additions - total_deletions} lines of code.")
        
        if file_types:
            primary_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)[:3]
            type_list = ', '.join([f"{t[0]} ({t[1]} files)" for t in primary_types])
            summary_parts.append(f"The changes primarily affect {type_list} files.")
        
        if key_files:
            top_files = [f.get('filename') for f in key_files[:3]]
            summary_parts.append(f"Key files modified include {', '.join(top_files)}.")
        
        # Add patch analysis insights about actual code changes
        if patch_analysis.get("features_detected"):
            features = ', '.join(patch_analysis['features_detected'][:3])
            summary_parts.append(f"Code review reveals the implementation includes: {features}.")
        
        if patch_analysis.get("change_patterns"):
            patterns = ', '.join(patch_analysis['change_patterns'][:2])
            summary_parts.append(f"The changes demonstrate {patterns}.")
        
        if body:
            description_preview = body[:200].replace('\n', ' ').strip()
            summary_parts.append(f"The PR description indicates: {description_preview}...")
        
        summary = " ".join(summary_parts)
        
        # Create detailed breakdown for reference
        details = f"\n\nDetailed Breakdown:\n"
        details += f"PR #{pr_number}: {pr_title}\n"
        details += f"Author: {author}\n"
        details += f"Status: {pr.get('state')}\n"
        details += f"Created: {pr.get('created_at')}\n"
        details += f"Files changed: {files_changed} | Additions: +{total_additions} | Deletions: -{total_deletions}\n"
        
        # Create comprehensive quality assessment
        total_changes = total_additions + total_deletions
        complexity = "high" if total_changes > 500 else "medium" if total_changes > 100 else "low"
        risk_level = "high" if files_changed > 20 else "medium" if files_changed > 5 else "low"
        
        quality_score = "excellent"
        quality_factors = []
        
        # Assess quality based on various factors
        if total_changes > 1000:
            quality_score = "needs_review"
            quality_factors.append("very large change set")
        elif total_changes < 50:
            quality_factors.append("focused change set")
        
        if files_changed > 15:
            if quality_score == "excellent":
                quality_score = "good"
            quality_factors.append("multiple files affected")
        elif files_changed <= 3:
            quality_factors.append("targeted file modifications")
        
        if body and len(body) > 100:
            quality_factors.append("detailed description provided")
        elif not body or len(body) < 50:
            if quality_score != "needs_review":
                quality_score = "good"
            quality_factors.append("description could be more detailed")
        
        quality_assessment = f"PR Quality Assessment: This pull request demonstrates {quality_score} quality. "
        if quality_factors:
            quality_assessment += "Key factors: " + ", ".join(quality_factors) + ". "
        quality_assessment += f"The change complexity is {complexity} ({total_changes} total changes across {files_changed} files), and the risk level is {risk_level}."
        
        review = {
            "complexity": complexity,
            "risk_level": risk_level,
            "quality_score": quality_score,
            "quality_assessment": quality_assessment,
            "recommendations": []
        }
        
        if total_changes > 1000:
            review["recommendations"].append("Large PR - consider breaking into smaller, focused changes for easier review")
        if files_changed > 15:
            review["recommendations"].append("Many files changed - ensure thorough testing across all affected areas")
        if not body or len(body) < 50:
            review["recommendations"].append("PR description could be enhanced with more context about the changes")
        if not review["recommendations"]:
            review["recommendations"].append("PR is well-structured and ready for review")
        
        # Combine summary with quality assessment
        full_summary = summary + " " + quality_assessment + details
        
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
            "summary": full_summary,
            "summary_paragraph": summary + " " + quality_assessment,  # Clean paragraph for display
            "review": review,
            "patch_analysis": patch_analysis  # NEW: Patch analysis with actual code changes
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

