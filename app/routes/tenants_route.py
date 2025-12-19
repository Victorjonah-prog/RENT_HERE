from sqlalchemy.orm import Session

from app.routes.users_route import raiseError
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
    prefix="/tenants",
    tags=["Tenants"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_tenant(tenant_request: User, db: Session = Depends(get_db)):

    userExists = db.query(users_model.Users).filter(
        (tenant_request.email == users_model.Users.email) | (tenant_request.phone == users_model.Users.phone)
    ).first()

    if userExists:
        raiseError("email or phone already exists")
    
    new_user = users_model.Users( **tenant_request.dict())

    try:  
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return new_user
    except pymysql.DataError as e:
        raiseError(e)
    except Exception as e:
        raiseError(e)