from pydantic import BaseModel, EmailStr
from typing import Optional, Any
from datetime import datetime, time

class LoginIn(BaseModel):
    email: EmailStr
    password: str

class TokenPairOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshIn(BaseModel):
    email: EmailStr
    refresh_token: str