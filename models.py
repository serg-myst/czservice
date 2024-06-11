from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Token(Base):
    __tablename__ = 'token_info'
    id = Column(Integer, primary_key=True)
    jwt_token = Column(Text)
    full_name = Column(String(250))
    inn = Column(String(12))
    mchd_id = Column(String(12))
    expiration_date = Column(DateTime)
