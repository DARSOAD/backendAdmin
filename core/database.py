from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cleaning:admin@localhost:5432/cleaning")

# Configurar conexión a PostgreSQL
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para modelos de SQLAlchemy
Base = declarative_base()
