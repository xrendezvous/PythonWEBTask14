from sqlalchemy.orm import Session
from src.database.models import User
from fastapi import HTTPException


def update_avatar(email: str, avatar_url: str, db: Session):
    """
    Update the avatar of a user identified by email.

    :param email: str, the email of the user whose avatar is to be updated
    :param avatar_url: str, the new URL of the avatar
    :param db: Session, the database session
    :return: The updated user object
    :raises HTTPException: 404 if the user is not found
    """
    user = db.query(User).filter(User.email == email).first()
    if user:
        user.avatar_url = avatar_url
        db.commit()
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")
