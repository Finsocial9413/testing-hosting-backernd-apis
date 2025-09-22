from fastapi import APIRouter, HTTPException, Depends, status, File, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from django.contrib.auth import authenticate, get_user_model
from django.core.exceptions import ValidationError
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from .models import HindAIUser, UserProfile
from .serializers import UserSerializer
from asgiref.sync import sync_to_async
from django.db import transaction
import os

router = APIRouter()

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    first_name: str
    last_name: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    first_name: str
    last_name: str
    token: Optional[str] = None
    is_staff: Optional[bool] = None
    is_superuser: Optional[bool] = None
    is_authenticated: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None

# JWT Configuration
SECRET_KEY = os.getenv('JWT_SECRET_KEY', "your-secret-key-here")  # Should be set in environment
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_EXPIRE_MINUTES', "30"))

# Security setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Helper functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Auth endpoints
@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate):
    UserModel = get_user_model()
    
    # Convert sync operations to async
    @sync_to_async
    def create_user():
        with transaction.atomic():
            # Check if user exists
            if UserModel.objects.filter(email=user_data.email).exists():
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
            
            # Create new user
            try:
                user = UserModel.objects.create(
                    email=user_data.email,
                    username=user_data.username,
                    first_name=user_data.first_name,
                    last_name=user_data.last_name
                )
                user.set_password(user_data.password)
                user.save()
                return user
            except Exception as e:
                raise HTTPException(
                    status_code=400,
                    detail=str(e)
                )
    
    try:
        user = await create_user()
        token = create_access_token({"sub": user.email})
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "token": token
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@router.post("/login", response_model=UserResponse)
async def login(user_data: OAuth2PasswordRequestForm = Depends()):
    UserModel = get_user_model()
    @sync_to_async
    def verify_user():
        try:
            # Try to get user by email first
            try:
                user = UserModel.objects.get(email=user_data.username)
            except UserModel.DoesNotExist:
                # If email not found, try username
                try:
                    user = UserModel.objects.get(username=user_data.username)
                except UserModel.DoesNotExist:
                    return None
                
            if user.check_password(user_data.password):
                return user
            return None
        except Exception:
            return None

    user = await verify_user()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": user.email})
    return {
        "id": user.id,
        "email": user.email,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "is_authenticated": True,
        "token": token
    }

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    
    user = HindAIUser.objects.filter(email=email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Profile Pydantic models
class ProfileData(BaseModel):
    phone_number: Optional[str] = None
    bio: Optional[str] = None
    twitter_handle: Optional[str] = None
    facebook_handle: Optional[str] = None
    linkedin_handle: Optional[str] = None
    instagram_handle: Optional[str] = None
    github_handle: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    profile_picture: Optional[str] = None

class UserProfileResponse(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    profile: Optional[ProfileData] = None

# Profile endpoints
@router.get("/profile/{username}", response_model=UserProfileResponse)
async def get_user_profile(username: str):
    @sync_to_async
    def get_profile():
        try:
            user = HindAIUser.objects.get(username=username)
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Get profile picture URL if exists
            profile_picture_url = None
            if profile.profile_picture:
                profile_picture_url = f"/media/{profile.profile_picture}"
            
            profile_data = {
                "phone_number": profile.phone_number,
                "bio": profile.bio,
                "twitter_handle": profile.twitter_handle,
                "facebook_handle": profile.facebook_handle,
                "linkedin_handle": profile.linkedin_handle,
                "instagram_handle": profile.instagram_handle,
                "github_handle": profile.github_handle,
                "location": profile.location,
                "website": profile.website,
                "profile_picture": profile_picture_url
            }
            
            return {
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "profile": profile_data
            }
        except HindAIUser.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return await get_profile()

@router.put("/profile/update/{username}", response_model=ProfileData)
async def update_user_profile(username: str, profile_data: ProfileData):
    @sync_to_async
    def update_profile():
        with transaction.atomic():
            try:
                user = HindAIUser.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Update fields if provided
                if profile_data.phone_number is not None:
                    profile.phone_number = profile_data.phone_number
                if profile_data.bio is not None:
                    profile.bio = profile_data.bio
                if profile_data.twitter_handle is not None:
                    profile.twitter_handle = profile_data.twitter_handle
                if profile_data.facebook_handle is not None:
                    profile.facebook_handle = profile_data.facebook_handle
                if profile_data.linkedin_handle is not None:
                    profile.linkedin_handle = profile_data.linkedin_handle
                if profile_data.instagram_handle is not None:
                    profile.instagram_handle = profile_data.instagram_handle
                if profile_data.github_handle is not None:
                    profile.github_handle = profile_data.github_handle
                if profile_data.location is not None:
                    profile.location = profile_data.location
                if profile_data.website is not None:
                    profile.website = profile_data.website
                
                profile.save()
                
                return {
                    "phone_number": profile.phone_number,
                    "bio": profile.bio,
                    "twitter_handle": profile.twitter_handle,
                    "facebook_handle": profile.facebook_handle,
                    "linkedin_handle": profile.linkedin_handle,
                    "instagram_handle": profile.instagram_handle,
                    "github_handle": profile.github_handle,
                    "location": profile.location,
                    "website": profile.website
                }
            except HindAIUser.DoesNotExist:
                raise HTTPException(status_code=404, detail="User not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    return await update_profile()

@router.post("/profile/upload-picture/{username}")
async def upload_profile_picture(username: str, file: UploadFile = File(...)):
    @sync_to_async
    def save_profile_picture():
        with transaction.atomic():
            try:
                user = HindAIUser.objects.get(username=username)
                profile, created = UserProfile.objects.get_or_create(user=user)
                
                # Save file
                file_location = f"media/profile_pictures/{username}_{file.filename}"
                os.makedirs(os.path.dirname(file_location), exist_ok=True)
                
                with open(file_location, "wb+") as f:
                    content = file.file.read()
                    f.write(content)
                
                # Update profile picture path
                profile.profile_picture = f"profile_pictures/{username}_{file.filename}"
                profile.save()
                
                return {
                    "success": True,
                    "username": username,
                    "filename": file.filename
                }
            except HindAIUser.DoesNotExist:
                raise HTTPException(status_code=404, detail="User not found")
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    return await save_profile_picture()







# Password update Pydantic model

# Password update Pydantic model
class PasswordUpdateData(BaseModel):
    old_password: str
    new_password: str

# Password update endpoint
# Password update endpoint
@router.put("/profile/update-password/{username}")
async def update_user_password(username: str, password_data: PasswordUpdateData):
    @sync_to_async
    def change_password():
        with transaction.atomic():
            try:
                # Find the user by username
                user = HindAIUser.objects.get(username=username)
                
                # Verify old password first
                if not user.check_password(password_data.old_password):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Current password is incorrect"
                    )
                
                # Update the password
                user.set_password(password_data.new_password)
                user.save()
                
                return {
                    "success": True,
                    "message": f"Password updated successfully for user {username}"
                }
            except HindAIUser.DoesNotExist:
                raise HTTPException(status_code=404, detail="User not found")
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    return await change_password()



# First, add this Pydantic model near your other model definitions
class UserUpdateData(BaseModel):
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Then add this endpoint
@router.put("/user/update/{current_username}", response_model=UserResponse)
async def update_user_info(current_username: str, user_data: UserUpdateData):
    @sync_to_async
    def update_user():
        with transaction.atomic():
            try:
                user = HindAIUser.objects.get(username=current_username)
                
                # Update fields if provided
                if user_data.username is not None:
                    # Check if the new username is already taken (if it's different from current)
                    if user_data.username != current_username:
                        if HindAIUser.objects.filter(username=user_data.username).exists():
                            raise HTTPException(
                                status_code=400,
                                detail="Username already taken"
                            )
                    user.username = user_data.username
                
                if user_data.first_name is not None:
                    user.first_name = user_data.first_name
                    
                if user_data.last_name is not None:
                    user.last_name = user_data.last_name
                
                user.save()
                
                # Generate a new token with updated information
                token = create_access_token({"sub": user.email})
                
                return {
                    "id": user.id,
                    "email": user.email,
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_staff": user.is_staff,
                    "is_superuser": user.is_superuser,
                    "is_authenticated": True,
                    "token": token
                }
            except HindAIUser.DoesNotExist:
                raise HTTPException(status_code=404, detail="User not found")
            except HTTPException as e:
                raise e
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
    
    return await update_user()