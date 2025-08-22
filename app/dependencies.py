from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db import get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.schemas import TokenData


async def get_current_user(token: str, db: AsyncSession = Depends(get_db)):
    # pylint: disable=import-outside-toplevel
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError as e:
        raise credentials_exception from e

    from app.routes.auth_routes import get_user_by_email

    user = await get_user_by_email(db, token_data.email)
    if not user:
        raise credentials_exception
    return user
