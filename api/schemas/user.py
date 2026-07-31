from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique login account name")
    email: EmailStr = Field(..., description="A verified, well-formed email address structure")
    password: str = Field(..., min_length=8, description="Plaintext raw user password to hash")

class UserLogin(BaseModel):
    username_or_email: str = Field(..., description="Accepts either registration credential identifier")
    password: str = Field(..., description="Plaintext authentication check string match")

class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True
