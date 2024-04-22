from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext

SECRET_KEY = "asecretkey8394"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict):
    """
    Create a JWT access token using the specified user data.

    :param data: dict, a dictionary containing data about the user and any additional claims
    :return: A JWT-encoded string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password, hashed_password):
    """
    Verify a password against a hashed password.

    :param plain_password: str, the plaintext password to verify
    :param hashed_password: str, the hashed password to verify against
    :return: bool, True if the password is correct, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """
    Generate a password hash for a given plaintext password.

    :param password: str, the plaintext password to hash
    :return: str, the hashed password
    """
    return pwd_context.hash(password)


def create_email_token(data: dict):
    """
    Create a JWT token for email verification purposes.

    :param data: dict, a dictionary containing the user's email and any additional claims
    :return: A JWT-encoded string
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=7)
    to_encode.update({"iat": datetime.utcnow(), "exp": expire})
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return token