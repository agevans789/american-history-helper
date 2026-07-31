from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Optional
from api.database import get_db
from api.models.users import SearchHistory
from api.schemas.discovery import UnifiedSearchResponseDTO, SearchResultDTO, RecommendationDTO

router = APIRouter(prefix='/api', tags=['Discovery'])

@router.get("/discover", response_model=UnifiedSearchResponseDTO)
async def discover_history(
    q: str = Query(..., description="Search query"),
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
        ORDER BY rank DESC
        LIMIT 10;
    """)
    search_result = await db.execute(search_sql, {'query': q})

    matching_sources, source_ids = [], []
    for row in search_result:
        matching_sources.append(SearchResultDTO(
            entry_id=row.entry_id,
            title=row.title,
            content=row.content,
            historical_era=row.historical_era,
            rank=float(row.rank)
        ))
        source_ids.append(row.entry_id)

    if not source_ids:
        return UnifiedSearchResponseDTO(
            query=q,
            matching_sources=[],
            recommended_topics=[]
        )

    discovery_sql = text("""
        SElECT DISTINCT ON (he.entry_id)
            he.entry_id, he.title, he.historical_era, r.relationship_type, r.weight
        FROM relationships r
        JOIN historical_entries he ON r.target_entry_id = he.entry_id
        WHERE r.source_entry_id = ANY(:source_ids) AND r.target_entry_id != ANY(:source_ids)
        ORDER BY he.entry_id, r.weight DESC LIMIT 6;
    """)
    discovery_result = await db.execute(discovery_sql, {'source_ids': source_ids})

    recommended_topics = []
    for row in discovery_result:
        recommended_topics.append(RecommendationDTO(
            entry_id=row.entry_id,
            title=row.title,
            historical_era=row.historical_era,
            relationship_type=row.relationship_type,
            weight=float(row.weight)
        ))

    return UnifiedSearchResponseDTO(
        query=q,
        matching_sources=matching_sources,
        recommended_topics=recommended_topics
    )