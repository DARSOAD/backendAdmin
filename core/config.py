import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cleaning:admin@localhost/cleaning")
SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
