from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate, UserOut
from app.schemas.token import Token
from app.crud.user import create_user, authenticate_user
from app.utils.security import create_access_token
from app.config.database import get_session

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(
    user_in: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    existing = await session.execute(
        select(User).where(
            (User.username == user_in.username) |
            (User.email == user_in.email)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username or email already registered")
    user = await create_user(session, user_in.username, user_in.email, user_in.password)
    return user

@router.post("/signin", response_model=Token)
async def signin(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}