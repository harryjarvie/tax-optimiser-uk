from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Local SQLite (later we'll switch to Postgres on Render)
SQLALCHEMY_DATABASE_URL = "sqlite:///./backend/app/data/app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to be used in routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()