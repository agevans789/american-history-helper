from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

router = APIRouter(prefix="/api", tags=["Discovery"])

class SearchResultDTO(BaseModel):
    entry_id: int
    title: str
    content: str
    historical_era: str
    rank: float

class RecommendationDTO(BaseModel):
    entry_id: int
    title: str
    historical_era: str
    relationship_type: str
    weight: float

class LocDocumentDTO(BaseModel):
    title: str
    url: str
    item_date: Optional[str] = "Unknown Date"
    description: Optional[str] = "No archival summary available."

class ExpandedDiscoveryResponse(BaseModel):
    query: str
    matching_sources: List[SearchResultDTO]
    recommended_topics: List[RecommendationDTO]
    loc_primary_sources: List[LocDocumentDTO]

def detect_historical_era(text_corpus: str) -> str:
    corpus = text_corpus.lower()
    if any(w in corpus for w in ["1776", "revolution", "stamp act", "washington", "colonial", "tecumseh"]):
        return "Revolutionary War & Early Republic Era"
    if any(w in corpus for w in ["1861", "1865", "lincoln", "civil war", "emancipation", "clay"]):
        return "Civil War & Antebellum Era"
    if any(w in corpus for w in ["rockefeller", "gilded", "monopoly", "trust", "oil", "standard", "twain"]):
        return "Gilded Age & Progressive Era"
    if any(w in corpus for w in ["1929", "depression", "hoover", "roosevelt", "new deal"]):
        return "The Great Depression Era"
    if any(w in corpus for w in ["1941", "pearl harbor", "wwii", "allied"]):
        return "World War II Era"
    if any(w in corpus for w in ["nixon", "watergate", "vietnam", "cold war", "197", "elvis", "monroe"]):
        return "Late 20th Century History"
    return "American History Archive Chronology"

@router.get("/discover", response_model=ExpandedDiscoveryResponse)
async def discover_history(
    q: str = Query(..., description="The historical search phrase"),
    user_id: Optional[int] = None
):
    clean_query = q.strip()
    title_case_query = clean_query.title()
    base_era = detect_historical_era(clean_query)
    

    matching_sources = [
        SearchResultDTO(
            entry_id=1001,
            title=f"Core Analytical Study: {title_case_query}",
            content=f"An integrated review of the strategic choices, operational turning points, and long-term legacy footprints of {title_case_query} inside American historical networks.",
            historical_era=base_era,
            rank=1.0
        )
    ]

    return ExpandedDiscoveryResponse(
        query=title_case_query,
        matching_sources=matching_sources,
        recommended_topics=[],
        loc_primary_sources=[]
    )



