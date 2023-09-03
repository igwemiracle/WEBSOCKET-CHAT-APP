from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from Authenticate.hash_pwd import HashPassword
from Authenticate.auth import oauth2_scheme
from Authenticate.jwt_handler import verify_access_token
from Database.connection import get_db
from Models.sqlData import User

HASH = HashPassword()


async def createRegisteredUser(username: str, email: str, hashed_password: str, db: AsyncSession):
    hash_this_pwd = HASH.create_hash(hashed_password)
    new_user = User(username=username, email=email,
                    hash_password=hash_this_pwd)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Sign in for access")

    decoded_token = verify_access_token(token)
    return decoded_token["username"]


async def get_user_by_email(email: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.email == email)
    result = await db.execute(query)
    return result.scalar()


async def get_user_by_username(username: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == username)
    result = await db.execute(query)
    return result.scalar()


async def findUser(username: str, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM websocket WHERE username=:username")
    result = await db.execute(query, {"username": username})
    return result.fetchone()


async def findRecipient(recipient: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == recipient)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def findSender(sender: str, db: AsyncSession = Depends(get_db)):
    query = select(User).where(User.username == sender)
    result = await db.execute(query)
    return result.scalar_one_or_none()
