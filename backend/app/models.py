from sqlalchemy import Column, Integer, String, Float
from .database import Base

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, index=True)
    track_number = Column(Integer, default=0) # NUEVO: Metadato de pista
    duration = Column(Float)
    path = Column(String, unique=True)
    file_size = Column(Float)
    bit_depth = Column(Integer)
    sample_rate = Column(Integer)
    bitrate = Column(Integer)
    added_at = Column(Float)