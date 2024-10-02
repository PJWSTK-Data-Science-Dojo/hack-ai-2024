from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    Float,
)
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    process_id = Column(String, index=True)
    stage = Column(String, default="uploaded")
    user_id = Column(Integer, ForeignKey("users.id"))
    perc = Column(Float, default=0.0)

    user = relationship("User", back_populates="videos")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    allowed_to_use = Column(Boolean, default=True)

    videos = relationship("Video", back_populates="user")


Base.metadata.create_all(bind=engine)
