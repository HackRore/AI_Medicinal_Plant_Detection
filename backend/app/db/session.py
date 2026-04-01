from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

DATABASE_URL = settings.DATABASE_URL

# Fix common URL prefix issue
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set in .env or settings.")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
    connect_args={"sslmode": "require"}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_connection():
    """Test DB connection on startup."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("Supabase PostgreSQL connected successfully")
        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False
