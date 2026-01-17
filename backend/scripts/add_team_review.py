#!/usr/bin/env python3
"""
Helper script to add a team review to the database
Usage: python scripts/add_team_review.py "Review text here" "Team Member Name"
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.db.database import SessionLocal, init_db
from app.models.team_review import TeamReview
from datetime import datetime

def add_team_review(text: str, team_member: str = None):
    """Add a team review to the database"""
    init_db()
    db = SessionLocal()
    
    try:
        review = TeamReview(
            text=text,
            team_member=team_member or "Anonymous"
        )
        db.add(review)
        db.commit()
        db.refresh(review)
        print(f"✅ Added team review #{review.id} from {review.team_member}")
        return review
    except Exception as e:
        db.rollback()
        print(f"❌ Error adding review: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/add_team_review.py \"Review text\" [Team Member Name]")
        sys.exit(1)
    
    text = sys.argv[1]
    team_member = sys.argv[2] if len(sys.argv) > 2 else None
    
    add_team_review(text, team_member)

