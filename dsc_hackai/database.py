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
    user_id = Column(Integer, ForeignKey("users.id"))
    perc = Column(Float, default=0.0)
    stage = Column(String, default="processing")

    analysis_stages = relationship("VideoAnalysis", back_populates="video")
    user = relationship("User", back_populates="videos")


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    allowed_to_use = Column(Boolean, default=True)

    videos = relationship("Video", back_populates="user")


class VideoAnalysis(Base):
    __tablename__ = "video_analysis"
    id = Column(Integer, primary_key=True, index=True)
    video_id = Column(Integer, ForeignKey("videos.id"))
    analysis = Column(String)
    stage = Column(String, default="started")
    data = Column(String)
    video = relationship("Video", back_populates="analysis_stages")


Base.metadata.create_all(bind=engine)
