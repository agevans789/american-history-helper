import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional, List
from pydantic import BaseModel
from api.database import get_db
from api.models.users import SearchHistory
from api.schemas.discovery import SearchResultDTO, RecommendationDTO

router = APIRouter(prefix="/api", tags=["Discovery"])

class LocDocumentDTO(BaseModel):
    title: str
    url: str
    item_date: Optional[str]
    description: Optional[str]

class ExpandedDiscoveryResponse(BaseModel):
    query: str
    matching_sources: List[SearchResultDTO]
    recommended_topics: List[RecommendationDTO]
    loc_primary_sources: List[LocDocumentDTO]

@router.get("/discover", response_model=ExpandedDiscoveryResponse)
async def discover_history(
    q: str = Query(..., description="The historical search phrase"),
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
):
 
    if user_id:
        try:
            db.add(SearchHistory(user_id=user_id, query_text=q))
            await db.flush() 
        except Exception:
            pass 


    search_sql = text("""
        SELECT entry_id, title, content, historical_era, 
               ts_rank(search_vector, websearch_to_tsquery('english', :query)) AS rank
        FROM historical_entries
        WHERE search_vector @@ websearch_to_tsquery('english', :query)
        ORDER BY rank DESC LIMIT 5;
    """)
    
    matching_sources, source_ids = [], []
    try:
        search_result = await db.execute(search_sql, {"query": q})
        for row in search_result:
            matching_sources.append(
                SearchResultDTO(
                    entry_id=row.entry_id, title=row.title, content=row.content,
                    historical_era=row.historical_era, rank=float(row.rank)
                )
            )
            source_ids.append(row.entry_id)
    except Exception as db_err:
        print(f"Database text search skipped (tables empty or unseeded yet): {db_err}")


    recommended_topics = []
    if source_ids:
        try:
            discovery_sql = text("""
                SELECT DISTINCT ON (he.entry_id) 
                    he.entry_id, he.title, he.historical_era, r.relationship_type, r.weight
                FROM relationships r
                JOIN historical_entries he ON r.target_entry_id = he.entry_id
                WHERE r.source_entry_id = ANY(:source_ids) AND r.target_entry_id != ANY(:source_ids)
                ORDER BY he.entry_id, r.weight DESC LIMIT 4;
            """)
            discovery_result = await db.execute(discovery_sql, {"source_ids": source_ids})
            for row in discovery_result:
                recommended_topics.append(
                    RecommendationDTO(
                        entry_id=row.entry_id, title=row.title, historical_era=row.historical_era,
                        relationship_type=row.relationship_type, weight=float(row.weight)
                    )
                )
        except Exception as graph_err:
            print(f"Graph recommendations skipped: {graph_err}")

  
    loc_primary_sources = []
    loc_url = "https://www.loc.gov/search/"
    params = {"q": q, "fo": "json", "c": 5}
    
    try:
        async with httpx.AsyncClient() as client:
            loc_response = await client.get(loc_url, params=params, timeout=5.0)
            if loc_response.status_code == 200:
                loc_data = loc_response.json()
                
                for item in loc_data.get("results", []):
                    raw_desc = item.get("description", "No archival description provided.")
                    if isinstance(raw_desc, list) and len(raw_desc) > 0:
                        desc_text = str(raw_desc[0])
                    else:
                        desc_text = str(raw_desc)
                    
                    raw_date = item.get("date", "Unknown Date")
                    if isinstance(raw_date, list) and len(raw_date) > 0:
                        date_text = str(raw_date[0])
                    else:
                        date_text = str(raw_date)

                    loc_primary_sources.append(
                        LocDocumentDTO(
                            title=str(item.get("title", "Untitled Archival Artifact Document")),
                            url=str(item.get("id", "https://www.loc.gov")),
                            item_date=date_text,
                            description=desc_text[:230] + "..." if len(desc_text) > 230 else desc_text
                        )
                    )
    except Exception as e:
        print(f"Library of Congress broker encountered an error: {e}")


    return ExpandedDiscoveryResponse(
        query=q,
        matching_sources=matching_sources,
        recommended_topics=recommended_topics,
        loc_primary_sources=loc_primary_sources
    )
