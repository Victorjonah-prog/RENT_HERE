import cloudinary
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import APIRouter, Form, HTTPException, UploadFile, status, Depends, File
from app.models import apartments_model, landlords_model
from app.schemas.users_schema import User
from app.schemas.apartments_schema import ApartmentResponse
from app.middlewares.auth import AuthMiddleware
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

@router.get("/", response_model=List[ApartmentResponse])
def get_apartments(db: Session = Depends(get_db)):
    apartments = db.query(apartments_model.Apartments).all()
    return apartments

@router.get("/{apartment_id}", response_model=List[ApartmentResponse])
def get_apartment(apartment_id: int, db: Session = Depends(get_db)):
    apartment = db.query(apartments_model.Apartment).filter(apartments_model.Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

@router.delete("/{apartment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_apartment(apartment_id: int, current_user: User = Depends(AuthMiddleware), db: Session = Depends(get_db)):
    apartment = db.query(apartments_model.Apartment).filter(apartments_model.Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    landlord = db.query(landlords_model.Landlords).filter_by(user_id=current_user.id).first()
    if not landlord or apartment.landlord_id != landlord.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this apartment")

    try:
        db.delete(apartment)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting apartment: {str(e)}")
    
@router.put("/{apartment_id}", response_model=List[ApartmentResponse])
def update_apartment(
    apartment_id: int,
    apartment_request: ApartmentResponse,
    current_user: User = Depends(AuthMiddleware),
    db: Session = Depends(get_db)
):
    apartment = db.query(apartments_model.Apartment).filter(apartments_model.Apartment.id == apartment_id).first()
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")

    landlord = db.query(landlords_model.Landlords).filter_by(user_id=current_user.id).first()
    if not landlord or apartment.landlord_id != landlord.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this apartment")

    try:
        apartment.name = apartment_request.name
        apartment.address = apartment_request.address
        apartment.description = apartment_request.description
        apartment.price = apartment_request.price

        db.commit()
        db.refresh(apartment)
        return apartment

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating apartment: {str(e)}")  