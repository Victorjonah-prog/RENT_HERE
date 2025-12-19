from sqlalchemy.orm import Session

from app.models import tenants_model
from app.routes.users_route import raiseError
from ..database import get_db
from fastapi import APIRouter, HTTPException, status, Depends
from ..models import users_model
from ..schemas.tenants_schema import Tenants
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
def create_tenant(tenant_request: Tenants, db: Session = Depends(get_db)):

    user = db.query(users_model.Users)\
        .filter_by(id=tenant_request.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    existing_tenant = db.query(tenants_model.Tenants)\
        .filter_by(user_id=tenant_request.user_id).first()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="User is already a tenant")

    
    new_tenant = tenants_model.Tenants(
        user_id=tenant_request.user_id,
        email=tenant_request.email
    )

    try:  
        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)

        return new_tenant
    except pymysql.DataError as e:
        raiseError(e)
    except Exception as e:
        raiseError(e)