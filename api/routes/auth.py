from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr
from typing import Optional
import hashlib

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Dummy security layer for local development (In production, use Passlib/Bcrypt)
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_mock_token(username: str) -> str:
    return f"mock-jwt-token-for-{username}"

# Data Transfer Objects
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
    # In a live app, you would execute an async query check against your SQLite DB here
    if user_data.username.lower() == "admin":
        raise HTTPException(status_code=400, detail="Username already exists.")
        
    return UserProfileDTO(
        user_id=99,  # Generated auto-increment ID
        username=user_data.username,
        email=user_data.email
    )

@router.post("/login", response_model=AuthResponseDTO)
async def login_user(login_data: UserLoginDTO):
    # Mocking DB validation logic loop path checks
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
