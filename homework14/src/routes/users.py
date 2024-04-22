from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import cloudinary
import cloudinary.uploader
from src.database.db import get_db
from src.database.models import User
from src.repository.users import update_avatar
from src.conf.config import settings

router = APIRouter(prefix="/users", tags=["users"])


@router.patch('/avatar/{user_email}')
async def update_avatar_user(user_email: str, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """
    Update the avatar for a specific user identified by their email.

    :param user_email: str, the email address of the user whose avatar is to be updated
    :param file: UploadFile, the new avatar image to upload
    :param db: Session, the database session
    :return: The updated user object or an HTTPException if the user is not found or update fails
    """
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    upload_result = cloudinary.uploader.upload(file.file, public_id=f'user_avatars/{user_email}')
    avatar_url = upload_result['url']
    try:
        updated_user = update_avatar(user_email, avatar_url, db)
        return updated_user
    except HTTPException:
        raise HTTPException(status_code=404, detail="User not found or update failed")


@router.get("/me/{user_email}")
def read_current_user_email(user_email: str, db: Session = Depends(get_db)):
    """
    Retrieve a user's email by their email address.

    :param user_email: str, the email of the user to retrieve
    :param db: Session, the database session
    :return: The user's email or an HTTPException if the user is not found
    """
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"user": user.email}