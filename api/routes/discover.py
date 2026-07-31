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
    item_date: Optional[str] = "Unknown Date"
    description: Optional[str] = "No archival summary available."

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

    matching_sources, source_ids = [], []
    try:
        search_sql = text("""
            SELECT entry_id, title, content, historical_era 
            FROM historical_entries
            WHERE title LIKE :like_query OR content LIKE :like_query
            LIMIT 5;
        """)
        
        search_result = await db.execute(search_sql, {"like_query": f"%{q}%"})
        for row in search_result:
            matching_sources.append(
                SearchResultDTO(
                    entry_id=row.entry_id, 
                    title=row.title, 
                    content=row.content,
                    historical_era=row.historical_era, 
                    rank=1.0 
                )
            )
            source_ids.append(row.entry_id)
    except Exception as db_err:
        print(f"Local SQLite extraction skipped (seeding required): {db_err}")

    recommended_topics = []
    if source_ids:
        try:
            discovery_sql = text("""
                SELECT DISTINCT he.entry_id, he.title, he.historical_era, r.relationship_type, r.weight
                FROM relationships r
                JOIN historical_entries he ON r.target_entry_id = he.entry_id
                WHERE r.source_entry_id IN :source_ids AND r.target_entry_id NOT IN :source_ids
                LIMIT 4;
            """)
            discovery_result = await db.execute(discovery_sql, {"source_ids": tuple(source_ids)})
            for row in discovery_result:
                recommended_topics.append(
                    RecommendationDTO(
                        entry_id=row.entry_id, title=row.title, historical_era=row.historical_era,
                        relationship_type=row.relationship_type, weight=float(row.weight)
                    )
                )
        except Exception as graph_err:
            print(f"Graph recommendations bypassed: {graph_err}")

    loc_primary_sources = []
    loc_url = "https://loc.gov"
    params = {"q": q, "fo": "json", "c": 3}
    
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            loc_response = await client.get(loc_url, params=params)
            if loc_response.status_code == 200:
                loc_data = loc_response.json()
                for item in loc_data.get("results", []):
                    raw_desc = item.get("description", "No archival description provided.")
                    desc_text = str(raw_desc) if isinstance(raw_desc, list) and len(raw_desc) > 0 else str(raw_desc)
                    
                    raw_date = item.get("date", "Unknown Date")
                    date_text = str(raw_date) if isinstance(raw_date, list) and len(raw_date) > 0 else str(raw_date)

                    title_raw = item.get("title", "Untitled Document Artifact")
                    id_raw = item.get("id", "https://loc.gov")

                    loc_primary_sources.append(
                        LocDocumentDTO(
                            title=str(title_raw) if isinstance(title_raw, list) and len(title_raw) > 0 else str(title_raw),
                            url=str(id_raw) if str(id_raw).startswith("http") else f"https:{id_raw}",
                            item_date=date_text,
                            description=desc_text[:230] + "..." if len(desc_text) > 230 else desc_text
                        )
                    )
    except Exception as network_error:
        print(f"LOC API offline or slow ({network_error}). Returning local data state layers.")

    return ExpandedDiscoveryResponse(
        query=q,
        matching_sources=matching_sources,
        recommended_topics=recommended_topics,
        loc_primary_sources=loc_primary_sources
    )

