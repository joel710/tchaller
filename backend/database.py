from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    is_verified = Column(Boolean, default=False)
    last_location = Column(Geometry(geometry_type='POINT', srid=4326))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Ambassador(Base):
    __tablename__ = "ambassadors"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    full_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="ambassador")

User.ambassador = relationship("Ambassador", back_populates="user", uselist=False)

class Merchant(Base):
    __tablename__ = "merchants"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("categories.id"))
    location = Column(Geometry(geometry_type='POINT', srid=4326), nullable=False)
    address = Column(String)
    phone_number = Column(String)
    whatsapp_number = Column(String)
    is_verified = Column(Boolean, default=False)
    is_open = Column(Boolean, default=True)
    opening_hours = Column(Text)  # JSON string for opening hours
    price_level = Column(Integer, default=1)  # 1-3 scale
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    ambassador_id = Column(Integer, ForeignKey("ambassadors.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Add spatial index
    __table_args__ = (
        Index('idx_merchant_location', 'location', postgresql_using='gist'),
    )

    category = relationship("Category", back_populates="merchants")
    ambassador = relationship("Ambassador", back_populates="merchants")
    photos = relationship("MerchantPhoto", back_populates="merchant")
    status_history = relationship("MerchantStatusHistory", back_populates="merchant")

Ambassador.merchants = relationship("Merchant", back_populates="ambassador")

class MerchantPhoto(Base):
    __tablename__ = "merchant_photos"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    image_url = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    merchant = relationship("Merchant", back_populates="photos")

class MerchantStatusHistory(Base):
    __tablename__ = "merchant_status_history"
    id = Column(Integer, primary_key=True, index=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    status = Column(String, nullable=False) # e.g., 'OPEN', 'CLOSED'
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    merchant = relationship("Merchant", back_populates="status_history")

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    merchants = relationship("Merchant", back_populates="category")

class SearchLog(Base):
    __tablename__ = "search_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query = Column(Text, nullable=False)
    location = Column(Geometry(geometry_type='POINT', srid=4326))
    results_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

User.conversations = relationship("Conversation", back_populates="user")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender = Column(String, nullable=False) # 'user' or 'bot'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    conversation = relationship("Conversation", back_populates="messages")

class Subscription(Base):
    __tablename__ = "subscriptions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")
    merchant = relationship("Merchant")

class Audit(Base):
    __tablename__ = "audits"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String, nullable=False)
    details = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User")

def create_db_and_tables():
    Base.metadata.create_all(bind=engine)