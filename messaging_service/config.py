import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "secret")
    MONGODB_URI = os.getenv("MONGODB_URI")
    DATABASE_NAME = os.getenv("DATABASE_NAME", "auth_database")
    EMAIL_FROM = os.getenv("BREVO_SENDER")
    BREVO_API_KEY = os.getenv("BREVO_API_KEY")