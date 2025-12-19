from sqlalchemy.orm import Session

from app.models import landlords_model
from app.routes.users_route import raiseError
from ..database import get_db
from fastapi import APIRouter, HTTPException, status, Depends
from ..models import users_model
from ..schemas.landlords_schema import Landlord
from ..middlewares.auth import AuthMiddleware
from datetime import datetime
from typing import List
import logging
import bcrypt
import pymysql

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/landlords",
    tags=["Landlords"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_landlord(landlord_request: Landlord, db: Session = Depends(get_db)):

    userExists = db.query(users_model.Users).filter(
        (landlord_request.email == users_model.Users.email).first()
    ).first()

    if userExists:
        raiseError("email or phone already exists")
    
    new_user = landlords_model.Landlords( **landlord_request.dict())

    try:  
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except pymysql.DataError as e:
        raiseError(e)
    except Exception as e:
        raiseError(e)