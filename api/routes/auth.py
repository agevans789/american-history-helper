from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_mock_token(username: str) -> str:
    return f"mock-jwt-token-for-{username}"

class UserRegisterDTO(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserLoginDTO(BaseModel):
    username: str
    password: str

class UserProfileDTO(BaseModel):
    user_id: int
    username: str
    email: str

class AuthResponseDTO(BaseModel):
    access_token: str
    token_type: str
    user: UserProfileDTO

@router.post("/register", response_model=UserProfileDTO, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegisterDTO):
    if user_data.username.lower() == "admin":
        raise HTTPException(status_code=400, detail="Username already exists.")
        
    return UserProfileDTO(
        user_id=99,  
        username=user_data.username,
        email=user_data.email
    )

@router.post("/login", response_model=AuthResponseDTO)
async def login_user(login_data: UserLoginDTO):
    if login_data.username == "testuser" and login_data.password == "password123":
        user_profile = UserProfileDTO(user_id=1, username="testuser", email="test@example.com")
        return AuthResponseDTO(
            access_token=generate_mock_token(login_data.username),
            token_type="bearer",
            user=user_profile
        )
    raise HTTPException(
        status_code=status.HTTP_412_PRECONDITION_FAILED,
        detail="Invalid username or password credentials configuration."
    )

@router.get("/profile", response_model=UserProfileDTO)
async def get_user_profile(token: str):
    if not token or "mock-jwt-token" not in token:
        raise HTTPException(status_code=401, detail="Invalid token session profile.")
    return UserProfileDTO(user_id=1, username="testuser", email="test@example.com")


class SavedSearchDTO(BaseModel):
    query_text: str

class FavoriteSourceDTO(BaseModel):
    title: str
    url: str
    description: Optional[str] = None


MOCK_SAVED_SEARCHES = []
MOCK_FAVORITE_SOURCES = []

@router.post("/saved-searches", status_code=201)
async def save_history_search(search_data: SavedSearchDTO, token: str):
    if not token or "mock-jwt-token" not in token:
        raise HTTPException(status_code=401, detail="Authentication token required.")
    
    
    record = {"search_id": len(MOCK_SAVED_SEARCHES) + 1, "query_text": search_data.query_text}
    MOCK_SAVED_SEARCHES.append(record)
    return {"message": f"Search phrase '{search_data.query_text}' saved successfully.", "data": record}

@router.get("/saved-searches")
async def list_saved_searches(token: str):
    if not token or "mock-jwt-token" not in token:
        raise HTTPException(status_code=401, detail="Authentication token required.")
    return MOCK_SAVED_SEARCHES

@router.post("/favorites", status_code=201)
async def favorite_historical_source(fav_data: FavoriteSourceDTO, token: str):
    if not token or "mock-jwt-token" not in token:
        raise HTTPException(status_code=401, detail="Authentication token required.")
        
    record = {
        "favorite_id": len(MOCK_FAVORITE_SOURCES) + 1,
        "title": fav_data.title,
        "url": fav_data.url,
        "description": fav_data.description
    }
    MOCK_FAVORITE_SOURCES.append(record)
    return {"message": "Primary resource book favorited securely.", "data": record}

@router.get("/favorites")
async def list_favorite_sources(token: str):
    if not token or "mock-jwt-token" not in token:
        raise HTTPException(status_code=401, detail="Authentication token required.")
    return MOCK_FAVORITE_SOURCES

@router.delete("/favorites/{favorite_id}")
async def delete_favorite_source(favorite_id: int, token: str):
    if not token or "mock-jwt-token" not in token:
        raise HTTPException(status_code=401, detail="Authentication token required.")
    
    global MOCK_FAVORITE_SOURCES
    MOCK_FAVORITE_SOURCES = [f for f in MOCK_FAVORITE_SOURCES if f["favorite_id"] != favorite_id]
    return {"message": "Favorite deleted."}

