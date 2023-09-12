from fastapi import HTTPException
from sqlalchemy import select, and_
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from Database.connection import get_db
from Models.schemas import MessageCreate
from Models.sqlData import SavedMessage
from Routes.crud import findUser

message_user = APIRouter()


@message_user.post("/send_message")
async def Messages(msg_crt: MessageCreate,
                   db: AsyncSession = Depends(get_db)):

    recipient_user = await findUser(user=msg_crt.recipient, db=db)
    if not recipient_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Recipient does not exist!")

    sender_user = await findUser(user=msg_crt.sender, db=db)
    if not sender_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Sender does not exist!")

    # Save the message to SavedMessage database
    saved_message = SavedMessage(
        sender_username=sender_user.username,
        recipient_username=recipient_user.username,
        text=msg_crt.text,
    )
    db.add(saved_message)
    await db.commit()
    return {
        "sender": msg_crt.sender,
        "text": msg_crt.text,
        "recipient": msg_crt.recipient,
    }


@message_user.get("/saved_messages/{username}")
async def getSavedMessages(username: str, db: AsyncSession = Depends(get_db)):

    check_user = await findUser(user=username, db=db)
    if not check_user:
        raise HTTPException(status_code=404, detail="User do not exist")

    saved_messages = await db.execute(
        select(SavedMessage).filter(
            or_(
                SavedMessage.sender_username == username,
                SavedMessage.recipient_username == username
            )
        )
    )
    return saved_messages.scalars().all()
# =================================================================================


@message_user.get("/saved_messages/{sender}/{recipient}")
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
