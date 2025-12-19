from sqlalchemy.orm import Session
from ..database import get_db
from fastapi import APIRouter, HTTPException, status, Depends
from ..models import users_model
from ..schemas.users_schema import User
from ..middlewares.auth import AuthMiddleware
from datetime import datetime
from typing import List
import logging
import bcrypt
import pymysql

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=User)
def create(user_request: User, db: Session = Depends(get_db)):

    userExists = db.query(users_model.Users).filter(
        (user_request.email == users_model.Users.email) | (user_request.phone == users_model.Users.phone)
    ).first()

    if userExists:
        raiseError("email or phone already exists")
    
    # salts = bcrypt.gensalt(rounds=12)
    # hashed_password = bcrypt.hashpw(user_request.password.encode('utf-8'), salts)
    
    new_user = users_model.Users(
        name=user_request.name,
        email=user_request.email,
        phone=user_request.phone,
        location=user_request.location,
        gender=user_request.gender
    )

    try:  
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except pymysql.DataError as e:
        raiseError(e)
    except Exception as e:
        raiseError(e)

def raiseError(e):
    logger.error(f"failed to create record error: {e}")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail = {
            "status": "error",
            "message": f"failed to create user: {e}",
            "timestamp": f"{datetime.utcnow()}"
        }
    )

@router.get("/", response_model=List[User])
def get_all_users(db: Session = Depends(get_db),
                  auth: AuthMiddleware = Depends()):
    users = db.query(users_model.Users).all()
    return users

@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: int, db: Session = Depends(get_db),
                   auth: AuthMiddleware = Depends()):
    user = db.query(users_model.Users).filter(users_model.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {
                "status": "error",
                "message": f"user with id {user_id} not found",
                "timestamp": f"{datetime.utcnow()}"
            }
        )
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db),
                auth: AuthMiddleware = Depends()):
    user = db.query(users_model.Users).filter(users_model.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {
                "status": "error",
                "message": f"user with id {user_id} not found",
                "timestamp": f"{datetime.utcnow()}"
            }
        )
    try:
        db.delete(user)
        db.commit()
    except Exception as e:
        raiseError(e)

@router.put("/{user_id}", response_model=User)
def update_user(user_id: int, user_request: User, db: Session = Depends(get_db),
                auth: AuthMiddleware = Depends()):
    user = db.query(users_model.Users).filter(users_model.Users.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail = {
                "status": "error",
                "message": f"user with id {user_id} not found",
                "timestamp": f"{datetime.utcnow()}"
            }
        )
    for key, value in user_request.dict().items():
        setattr(user, key, value)
    try:
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        raiseError(e)

