from sqlalchemy.orm import Session

from app.models import tenants_model
from app.routes.users_route import raiseError
from app.database import get_db
from fastapi import APIRouter, HTTPException, status, Depends
from app.models import users_model
from app.schemas.tenants_schema import Tenants
from app.middlewares.auth import AuthMiddleware
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
def create_tenant(
    tenant_request: Tenants,
    current_user = Depends(AuthMiddleware),
    db: Session = Depends(get_db),
):
    if tenant_request.email != current_user.email:
        raise HTTPException(
            status_code=403,
            detail="Email must match your account email"
        )

    existing_tenant = db.query(tenants_model.Tenants).filter(
        tenants_model.Tenants.user_id == current_user.id
    ).first()

    if existing_tenant:
        raise HTTPException(
            status_code=400,
            detail="Tenant already exists for this user"
        )

    new_tenant = tenants_model.Tenants(
        email=current_user.email,
        user_id=current_user.id
    )

    try:
        db.add(new_tenant)
        db.commit()
        db.refresh(new_tenant)
        return new_tenant

    except Exception as e:
        raiseError(e)
