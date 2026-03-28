# Redirection for backward compatibility with the new db/session.py
from app.db.session import engine, SessionLocal, Base, get_db, test_connection
