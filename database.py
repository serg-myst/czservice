from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL, echo=False, client_encoding='utf8')
session_maker = sessionmaker(engine, expire_on_commit=False)
