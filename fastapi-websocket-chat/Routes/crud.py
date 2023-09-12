from fastapi import Depends, HTTPException, status
from Models.sqlData import SavedMessage
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text, or_, and_
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


async def findUser(user: str, db: AsyncSession = Depends(get_db)):
    query = text("SELECT * FROM users WHERE username=:username")
    result = await db.execute(query, {"username": user})
    return result.fetchone()


async def getChatHistory(sender: str, recipient: str, db: AsyncSession = Depends(get_db)):

    check_sender = await findUser(user=sender, db=db)
    if not check_sender:
        raise HTTPException(status_code=404, detail="Sender does not exist")

    check_recipient = await findUser(user=recipient, db=db)
    if not check_recipient:
        raise HTTPException(status_code=404, detail="Recipient does not exist")

    messages = await db.execute(
        select(SavedMessage.sender_username, SavedMessage.text)
        .filter(
            or_(
                and_(
                    SavedMessage.sender_username == check_sender.username,
                    SavedMessage.recipient_username == check_recipient.username
                ),
                and_(
                    SavedMessage.sender_username == check_recipient.username,
                    SavedMessage.recipient_username == check_sender.username
                )
            )
        )
    )

    chat_history = [
        f"{message[0]}: {message[1]}" for message in messages.fetchall()]
    return chat_history
