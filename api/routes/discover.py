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
        keywords = q.strip().split()
        
        conditions = []
        query_params = {}
        for idx, word in enumerate(keywords):
            param_key = f"word_{idx}"
            conditions.append(f"(title LIKE :{param_key} OR content LIKE :{param_key})")
            query_params[param_key] = f"%{word}%"
            
        search_condition_string = " AND ".join(conditions) if conditions else "1=1"
        
        search_sql = text(f"""
            SELECT entry_id, title, content, historical_era 
            FROM historical_entries
            WHERE {search_condition_string}
            LIMIT 5;
        """)
        
        search_result = await db.execute(search_sql, query_params)
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
        print(f"Local SQLite extraction skipped: {db_err}")


    recommended_topics = []
    if source_ids:
        try:
            in_params = {f"id_{i}": sid for i, sid in enumerate(source_ids)}
            placeholders = ", ".join(f":{key}" for key in in_params.keys())
            
            discovery_query_string = f"""
                SELECT DISTINCT he.entry_id, he.title, he.historical_era, r.relationship_type, r.weight
                FROM relationships r
                JOIN historical_entries he ON r.target_entry_id = he.entry_id
                WHERE r.source_entry_id IN ({placeholders}) AND r.target_entry_id NOT IN ({placeholders})
                LIMIT 4;
            """
            
            discovery_result = await db.execute(text(discovery_query_string), in_params)
            for row in discovery_result:
                recommended_topics.append(
                    RecommendationDTO(
                        entry_id=row.entry_id, 
                        title=row.title, 
                        historical_era=row.historical_era,
                        relationship_type=row.relationship_type, 
                        weight=float(row.weight)
                    )
                )
        except Exception as graph_err:
            print(f"Graph recommendations bypassed: {graph_err}")


    loc_primary_sources = []
    loc_url = "https://www.loc.gov/search/"
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
                    id_raw = item.get("id", "https://www.loc.gov")

                    loc_primary_sources.append(
                        LocDocumentDTO(
                            title=str(title_raw) if not isinstance(title_raw, list) else str(title_raw[0]),
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


