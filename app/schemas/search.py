# app/schemas/search.py
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from enum import Enum


class SearchScope(str, Enum):
    """Search scope enumeration."""
    products = "products"
    customers = "customers"
    documents = "documents"
    all = "all"


class SearchRequest(BaseModel):
    """Search request schema."""
    query: str
    scope: SearchScope = SearchScope.all
    limit: int = 50
    filters: Optional[Dict[str, Any]] = None


class SearchResult(BaseModel):
    """Individual search result."""
    id: int
    type: str  # product, customer, document, etc.
    title: str
    description: Optional[str]
    relevance_score: float
    data: Dict[str, Any]


class SearchResponse(BaseModel):
    """Search response schema."""
    query: str
    scope: str
    total_results: int
    results: List[SearchResult]
    facets: Optional[Dict[str, Any]] = None  # For filtering
    suggestions: List[str] = []  # Query suggestions
