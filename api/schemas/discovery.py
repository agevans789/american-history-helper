from pydantic import BaseModel
from typing import List, Optional

class SearchResultDTO(BaseModel):
    entry_id: int
    title: str
    content: str
    historical_era: Optional[str]
    rank: float

class RecommendationDTO(BaseModel):
    entry_id: int
    title: str
    historical_era: Optional[str]
    relationship_type: Optional[str]
    weight: float    

class UnifiedSearchResponseDTO(BaseModel):
    query: str
    matching_entries: List[SearchResultDTO]
    recommended_topics: List[RecommendationDTO]