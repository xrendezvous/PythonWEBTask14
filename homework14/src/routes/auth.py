from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from src.database.db import get_db
from src.database.models import User
from src.schemas import UserCreate, Token
from src.services.auth import create_access_token, get_password_hash, verify_password
from src.services.email_verification import send_email


router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user in the system.

    :param user: UserCreate, the user data transfer object containing email and password
    :param db: Session, the database session
    :return: A token response with the new user's access token
    :raises HTTPException: 409 if email is already registered
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed_password = get_password_hash(user.password)
    db_user = User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    host_url = "http://127.0.0.1:8000/"
    await send_email(user.email, host_url)
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token, status_code=status.HTTP_201_CREATED)
def login(user: UserCreate, db: Session = Depends(get_db)):
    """
    Authenticate a user and return an access token.

    :param user: UserCreate, the user login data transfer object
    :param db: Session, the database session
    :return: A token response with the user's access token
    :raises HTTPException: 401 if the login credentials are invalid
    """
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}

