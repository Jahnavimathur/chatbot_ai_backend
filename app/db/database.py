import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

# The database might not exist yet, so we connect to the server without a DB name first
# to create it, then we create the engine with the database.
DB_URL_SERVER = "mysql+pymysql://root:@localhost:3306"
DATABASE_NAME = "chatbot_ai"
SQLALCHEMY_DATABASE_URL = f"{DB_URL_SERVER}/{DATABASE_NAME}"

# First, attempt to create the database if it doesn't exist
try:
    engine_server = create_engine(DB_URL_SERVER)
    with engine_server.connect() as conn:
        conn.execute(f"CREATE DATABASE IF NOT EXISTS {DATABASE_NAME}")
except Exception as e:
    print(f"Error creating database: {e}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
