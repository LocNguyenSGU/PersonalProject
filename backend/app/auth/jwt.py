"""
JWT Authentication Module
Provides token generation and validation for admin endpoints
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings
from app.utils.logger import logger

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 hours

# Bearer token security
security = HTTPBearer()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token
    
    Args:
        data: Payload to encode (typically {"sub": "admin"})
        expires_delta: Token expiration time (default: 8 hours)
    
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    
    try:
        encoded_jwt = jwt.encode(to_encode, settings.ADMIN_SECRET, algorithm=ALGORITHM)
        logger.info("Access token created successfully")
        return encoded_jwt
    except Exception as e:
        logger.error(f"Failed to create access token: {e}")
        raise HTTPException(status_code=500, detail="Could not create access token")

def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
    Verify JWT token from Authorization header
    
    Args:
        credentials: HTTP Bearer credentials from request header
    
    Returns:
        Decoded token payload
    
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        payload = jwt.decode(token, settings.ADMIN_SECRET, algorithms=[ALGORITHM])
        
        # Check token expiration
        exp = payload.get("exp")
        if exp is None:
            raise HTTPException(status_code=401, detail="Token missing expiration")
        
        if datetime.fromtimestamp(exp) < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Token expired")
        
        logger.info("Token verified successfully")
        return payload
        
    except JWTError as e:
        logger.warning(f"Token verification failed: {e}")
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

def verify_admin(credentials: HTTPAuthorizationCredentials = Security(security)) -> bool:
    """
    FastAPI dependency for protecting admin endpoints
    
    Usage:
        @router.get("/admin/endpoint", dependencies=[Depends(verify_admin)])
        async def admin_endpoint():
            return {"data": "protected"}
    
    Returns:
        True if valid admin token
    
    Raises:
        HTTPException: If unauthorized
    """
    payload = verify_token(credentials)
    
    # Check if token has admin role
    role = payload.get("sub")
    if role != "admin":
        logger.warning(f"Non-admin attempted to access admin endpoint: {role}")
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    return True
