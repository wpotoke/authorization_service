from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.core.security import get_email_from_token
from app.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
refresh_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
):
    # pylint: disable=import-outside-toplevel
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    email = get_email_from_token(token)

    if not email:
        raise credentials_exception

    token_data = TokenData(email=email)

    from app.routes.auth_routes import get_user_by_email

    user = await get_user_by_email(db, token_data.email)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


async def get_refresh_token(credentials: HTTPBearer = Depends(refresh_scheme)) -> str:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return credentials.credentials
