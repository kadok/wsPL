import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    
    DB_LINK = os.getenv("DB_LINK")
    DATABASE = os.getenv("DATABASE")
    COLLECTION = os.getenv("COLLECTION")
    DATA = os.getenv("DATA")