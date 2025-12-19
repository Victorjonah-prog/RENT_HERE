import cloudinary
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi import APIRouter, Form, HTTPException, UploadFile, status, Depends, File
from ..models import apartments_model, landlords_model
from ..schemas.users_schema import User
from ..middlewares.auth import AuthMiddleware
from datetime import datetime
from typing import List
import logging
import bcrypt
import pymysql

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/apartments",
    tags=["Apartments"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_apartment(
    name: str = Form(...),
    image: UploadFile = File(...),
    address: str = Form(...),
    description: str = Form(...),
    price: str = Form(...),
    current_user: User = Depends(AuthMiddleware),
    db: Session = Depends(get_db)
):

    landlord = db.query(landlords_model.Landlords).filter_by(user_id=current_user.id).first()
    if not landlord:
        raise HTTPException(status_code=403, detail="User is not a landlord")


    # Validate image type
    allowed_ext = {"jpg", "jpeg", "png"}
    file_ext = image.filename.split(".")[-1].lower() 
    if file_ext not in allowed_ext:
        raise HTTPException(status_code=400, detail="Only jpg/jpeg/png allowed")

    # Validate file type
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image contents
    contents = await image.read()
    
    # Check size (2MB limit)
    image_size = 2 * 1024 * 1024
    if len(contents) > image_size:
        raise HTTPException(status_code=400, detail="Image size exceeds 2 MB limit")

    # Upload to Cloudinary
    try:
        result = cloudinary.uploader.upload(
            contents,
            folder=f"renthere/apartments/{landlord.id}",
            resource_type="auto",
            transformation=[
                {"width": 800, "height": 800, "crop": "limit"},
                {"quality": "auto"}
            ]
        )
        image_url = result["secure_url"]
        cloudinary_public_id = result["public_id"]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")



    new_apartment = apartments_model.Apartment(
        landlord_id=landlord.id,
        name=name,
        image_url=image_url,
        address=address,
        description=description,
        price=float(price),
    )

    db.add(new_apartment)
    db.commit()
    db.refresh(new_apartment)

    return {
        "success": True,
        "message": "Apartment created successfully!",
        "apartment": new_apartment,
        "image_url": image_url
    }