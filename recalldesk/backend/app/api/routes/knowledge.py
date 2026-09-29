"""
Knowledge base API endpoints.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database.db import get_db
from app.models import KnowledgeArticle
from app.tools.support_tools import search_knowledge_base

router = APIRouter(prefix="/knowledge", tags=["knowledge"])


@router.get("")
def list_articles(
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """List all knowledge base articles."""
    q = db.query(KnowledgeArticle)
    if category:
        q = q.filter(KnowledgeArticle.category == category)
    articles = q.order_by(KnowledgeArticle.title).all()
    return {"articles": [a.to_dict() for a in articles], "count": len(articles)}


@router.get("/search")
def search_articles(
    q: str,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Search knowledge base articles."""
    result = search_knowledge_base(db, q, category)
    return result


@router.get("/{article_id}")
def get_article(article_id: str, db: Session = Depends(get_db)):
    from fastapi import HTTPException
    article = db.query(KnowledgeArticle).filter(KnowledgeArticle.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article.to_dict()
