import httpx
from urllib.parse import quote_plus
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

class ArchiveDocumentDTO(BaseModel):
    title: str
    url: str
    item_date: Optional[str] = "Unknown Date"
    description: Optional[str] = "No archival summary available."

class RecommendationDTO(BaseModel):
    entry_id: int
    title: str
    historical_era: str
    relationship_type: str
    weight: float
    archive_sources: List[ArchiveDocumentDTO] = []

class ExpandedDiscoveryResponse(BaseModel):
    query: str
    matching_sources: List[SearchResultDTO]
    recommended_topics: List[RecommendationDTO]
    archive_primary_sources: List[ArchiveDocumentDTO]

def detect_historical_era(text_corpus: str) -> str:
    corpus = text_corpus.lower()
    if any(w in corpus for w in ["nixon", "watergate", "vietnam", "197"]):
        return "Late 20th Century History"
    if any(w in corpus for w in ["1929", "depression", "hoover", "roosevelt", "193"]):
        return "The Great Depression Era"
    if any(w in corpus for w in ["twain", "gilded", "rockefeller", "188", "189"]):
        return "Gilded Age & Progressive Era"
    return "American History Archive Chronology"

def calculate_decade_themes(query: str, era_name: str) -> List[RecommendationDTO]:
    text = f"{query} {era_name}".lower()
    if "nixon" in text or "197" in text:
        return [
            RecommendationDTO(entry_id=3001, title="1970s Counterculture & Disco Style", historical_era=era_name, relationship_type="Style of the Era", weight=0.95),
            RecommendationDTO(entry_id=3002, title="Microprocessors & Early Home Computers", historical_era=era_name, relationship_type="Technology of the Time", weight=0.91),
            RecommendationDTO(entry_id=3003, title="New Journalism & Postmodern American Literature", historical_era=era_name, relationship_type="Literature of the Era", weight=0.88),
            RecommendationDTO(entry_id=3004, title="Funk, Funk Rock, Soul, & Progressive Rock", historical_era=era_name, relationship_type="Music of the Era", weight=0.85)
        ]
    if "depression" in text or "193" in text:
        return [
            RecommendationDTO(entry_id=3005, title="Art Deco Design & WPA Murals", historical_era=era_name, relationship_type="Style of the Era", weight=0.95),
            RecommendationDTO(entry_id=3006, title="Commercial Radio Networks & Sound Cinema", historical_era=era_name, relationship_type="Technology of the Time", weight=0.91),
            RecommendationDTO(entry_id=3007, title="The Grapes of Wrath & Social Realism Literature", historical_era=era_name, relationship_type="Literature of the Era", weight=0.88),
            RecommendationDTO(entry_id=3008, title="Big Band Swing, Delta Blues, & Urban Folk Music", historical_era=era_name, relationship_type="Music of the Era", weight=0.85)
        ]
    if "twain" in text or "gilded" in text or "188" in text or "189" in text:
        return [
            RecommendationDTO(entry_id=3009, title="Victorian Architecture & Gilded Opulence Style", historical_era=era_name, relationship_type="Style of the Era", weight=0.95),
            RecommendationDTO(entry_id=3010, title="Incandescent Lighting & Electric Power Grids", historical_era=era_name, relationship_type="Technology of the Time", weight=0.91),
            RecommendationDTO(entry_id=3011, title="Literary Realism & Regional American Dialects", historical_era=era_name, relationship_type="Literature of the Era", weight=0.88),
            RecommendationDTO(entry_id=3012, title="Classical Orchestras, Early Marching Bands, & Parlor Music", historical_era=era_name, relationship_type="Music of the Era", weight=0.85)
        ]
    return [
        RecommendationDTO(entry_id=3099, title=f"{query.title()} Material Culture & Style", historical_era=era_name, relationship_type="Style of the Era", weight=0.92),
        RecommendationDTO(entry_id=3100, title=f"{query.title()} Scientific & Industrial Tools", historical_era=era_name, relationship_type="Technology of the Time", weight=0.89),
        RecommendationDTO(entry_id=3101, title=f"{query.title()} Print Culture, Journals & Poetry", historical_era=era_name, relationship_type="Literature of the Era", weight=0.86),
        RecommendationDTO(entry_id=3102, title=f"{query.title()} Contemporary Sonic & Folk Traditions", historical_era=era_name, relationship_type="Music of the Era", weight=0.83)
    ]

async def search_archive(query: str, limit: int = 10) -> List[ArchiveDocumentDTO]:
    archive_results = []
    encoded_query = quote_plus(query)
    archive_api_url = "https://archive.org/advancedsearch.php"
    query_params = {
        "q": f"{query} AND mediatype:texts",
        "fl[]": ["identifier", "title", "date", "description"],
        "rows": limit,
        "output": "json"
    }

    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            response = await client.get(archive_api_url, params=query_params)
            if response.status_code == 200:
                data = response.json()
                docs = data.get("response", {}).get("docs", [])
                for idx, item in enumerate(docs, start=1):
                    formatted_title = item.get("title", f"Internet Archive Record {idx}")
                    raw_date = item.get("date", "")
                    display_date = "Archival Print"
                    if len(raw_date) >= 10:
                        display_date = raw_date[:10]
                    raw_desc = item.get("description", "")
                    clean_desc = str(raw_desc)[:220] + "..." if raw_desc else "Authentic library text sheet capturing primary source documentation records."
                    target_path = item.get("identifier", "")
                    if target_path:
                        true_url = f"https://archive.org/details/{target_path}"
                    else:
                        true_url = f"https://archive.org/search.php?query={encoded_query}"
                    archive_results.append(
                        ArchiveDocumentDTO(
                            title=formatted_title,
                            url=true_url,
                            item_date=display_date,
                            description=clean_desc
                        )
                    )
    except Exception:
        pass
    return archive_results

@router.get("/discover", response_model=ExpandedDiscoveryResponse)
async def discover_history(
    q: str = Query(..., description="The historical search phrase"),
    user_id: Optional[int] = None
):
    clean_query = q.strip()
    title_case_query = clean_query.title()
    base_era = detect_historical_era(clean_query)
    

    archive_primary_sources = await search_archive(clean_query)
    
    matching_sources = [
        SearchResultDTO(
            entry_id=1001,
            title=f"Core Analytical Study: {title_case_query}",
            content=f"An integrated review of the choices, operational turning points, and long-term legacy footprints of {title_case_query} inside American historical networks.",
            historical_era=base_era,
            rank=1.0
        )
    ]
    
    recommended_topics = calculate_decade_themes(clean_query, base_era)


    for topic in recommended_topics:
        topic.archive_sources = await search_archive(
            f"{topic.title} {base_era}",
            limit=5  
        )

    return ExpandedDiscoveryResponse(
        query=title_case_query,
        matching_sources=matching_sources,
        recommended_topics=recommended_topics,
        archive_primary_sources=archive_primary_sources
    )









