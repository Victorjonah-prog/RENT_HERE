from fastapi import FastAPI, status, HTTPException
from .models.base import Base
from .database import engine
from .models.users_model import Users
from .models.apartments_model import Apartments
from .models.landlords_model import Landlords
from .models.tenants_model import Tenants
import os
from sqlalchemy.exc import OperationalError
from fastapi.middleware.cors import CORSMiddleware
from .routes import users_route, oauth_route, landlords_routes, tenants_route, apartment_routes
from fastapi.staticfiles import StaticFiles
import time
from starlette.middleware.sessions import SessionMiddleware
from app.config import cloudinary
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def db_and_table_init():
    retries = 10
    for i in range(retries):
        try:
            logger.info("STARTING APPLICATION!")
            Base.metadata.create_all(bind=engine)
            logger.info("DATABASE INITIALIZED SUCCESSFULLY!")
            break
        except OperationalError as e:
            logger.warning(f"MySQL NOT READY, RETRYING ({i+1}/{retries}) {e}...")
            time.sleep(3)
        except Exception as e:
            logger.info(f"DATABASE INITIALIZATION FAILED: {e}")



app = FastAPI(
    title = "Rent_Here App",
    version = "0.0.1",
    description = "Rent place..."
    )



app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('JWT_SECRET_KEY'),
    https_only=False
)


origins = [
    "http://localhost:8000"


]

app.add_middleware(CORSMiddleware,allow_origins=origins,
                   allow_credentials=True,
                   allow_methods = ["*"],
                   allow_headers = ["*"]

                   )


app.include_router(users_route.router)
app.include_router(oauth_route.router)
app.include_router(apartment_routes.router)
app.include_router(landlords_routes.router)
app.include_router(tenants_route.router)



app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def on_startup():
    db_and_table_init()

@app.get("/")
def home():
    return{
        "status":"success",
        "message":"hello world"
    }

   


