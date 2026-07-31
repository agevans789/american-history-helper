from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from api.database import get_db
from api.models.users import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str

    class Config:
        from_attributes = True

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):

    existing_user_query = await db.execute(
        select(User).where((User.username == user_data.username) | (User.email == user_data.email))
    )
    if existing_user_query.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already registered")


    mock_hash = f"hashed_{user_data.password}"

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=mock_hash
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
