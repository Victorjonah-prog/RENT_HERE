from sqlalchemy.orm import Session

from app.models import landlords_model
from app.routes.users_route import raiseError
from app.database import get_db
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import users_model
from app.schemas.landlords_schema import Landlord
from app.middlewares.auth import AuthMiddleware
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
def create_landlord(landlord_request: Landlord,current_user = Depends(AuthMiddleware), db: Session = Depends(get_db)):

    userExists = db.query(landlords_model.Landlords).filter(
        (landlords_model.Landlords.user_id == current_user.id)
    ).first()

    if userExists:
        raiseError("email or phone already exists")
    
    new_landlord = landlords_model.Landlords( 
        user_id=current_user.id,
        email=landlord_request.email
    )

    try:  
        db.add(new_landlord)
        db.commit()
        db.refresh(new_landlord)

        return new_landlord
    except pymysql.DataError as e:
        raiseError(e)
    except Exception as e:
        raiseError(e)