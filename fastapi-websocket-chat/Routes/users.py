from fastapi import Depends, HTTPException, Request, APIRouter, status
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from Authenticate.hash_pwd import HashPassword
from Authenticate.jwt_handler import create_access_token
from Database.connection import get_db
from Models.schemas import UserCreate, BaseUser, Token
from Routes.crud import createRegisteredUser, get_user_by_email, findUser

templates = Jinja2Templates(directory="templates")
user = APIRouter()
HASH = HashPassword()


@user.get("/")
async def renderPage(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})


@user.post("/auth/signup", response_model=BaseUser)
async def SignUp(user: UserCreate,
                 db: AsyncSession = Depends(get_db)):
    user_exist = await get_user_by_email(email=user.email, db=db)
    if user_exist:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email address is already in use. Please choose another email or log in.")

    create_user = await createRegisteredUser(username=user.username,
                                             email=user.email,
                                             hashed_password=user.password,
                                             db=db)
    return create_user


@user.post("/auth/signin/", response_model=Token)
async def LoginPage(auth: UserCreate,
                    db: AsyncSession = Depends(get_db)) -> dict:
    user = await findUser(auth.username, db=db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed. Please check your email and password and try again!")

    if HASH.verify_hash(auth.password, user.hash_password):
        access_token = create_access_token(
            user.username, user.hash_password)

        return {
            "access_token": access_token,
            "token_type": "Bearer"
        }
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication failed. Please check your email and password and try again!"
    )
