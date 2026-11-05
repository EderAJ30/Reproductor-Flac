from fastapi import FastAPI, BackgroundTasks, Response, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading
import os
from mutagen.flac import FLAC
from sqlalchemy import create_engine, Column, Integer, String, Float, or_, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/db/flac_metadata.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Track(Base):
    __tablename__ = "tracks"
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, index=True)
    duration = Column(Float)
    path = Column(String, unique=True)
    file_size = Column(Float)
    bit_depth = Column(Integer)
    sample_rate = Column(Integer)
    bitrate = Column(Integer)
    added_at = Column(Float)

Base.metadata.create_all(bind=engine)
MUSIC_DIR = os.getenv("MUSIC_DIR", "/music")

def scan_directory_task():
    print("Iniciando escaneo de directorio...", flush=True)
    db = SessionLocal()
    try:
        contador = 0
        for root, dirs, files in os.walk(MUSIC_DIR):
            for file in files:
                if file.lower().endswith(".flac") and not file.startswith("."):
                    filepath = os.path.join(root, file)
                    if not db.query(Track).filter(Track.path == filepath).first():
                        try:
                            audio = FLAC(filepath)
                            track = Track(
                                filename=file,
                                title=audio.get("title", [file])[0],
                                artist=audio.get("artist", ["Desconocido"])[0],
                                album=audio.get("album", ["Desconocido"])[0],
                                duration=audio.info.length if hasattr(audio, 'info') else 0.0,
                                path=filepath,
                                file_size=os.path.getsize(filepath),
                                bit_depth=getattr(audio.info, 'bits_per_sample', 16),
                                sample_rate=getattr(audio.info, 'sample_rate', 44100),
                                bitrate=getattr(audio.info, 'bitrate', 0),
                                added_at=os.path.getmtime(filepath)
                            )
                            db.add(track)
                            db.commit() # AHORA GUARDAMOS CANCIÓN POR CANCIÓN
                            contador += 1
                            print(f"Indexado ({contador}): {file}", flush=True)
                        except Exception as e:
                            print(f"Error procesando {file}: {e}", flush=True)
        print("Escaneo finalizado exitosamente.", flush=True)
    finally:
        db.close()

# ESTO ES LO NUEVO: Arranca el escaneo automáticamente
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Se ejecuta al iniciar el contenedor
    hilo_escaneo = threading.Thread(target=scan_directory_task)
    hilo_escaneo.start()
    yield
    # Se ejecuta al apagar el contenedor
    print("Apagando API...")

app = FastAPI(title="FLAC Player API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/scan")
def start_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(scan_directory_task)
    return {"status": "ok", "message": "Escaneo iniciado desde el frontend."}

@app.get("/api/tracks")
def get_tracks(
    search: str = Query(None, description="Término de búsqueda"),
    sort: str = Query("recent", description="recent, size_asc, size_desc"),
    skip: int = 0, 
    limit: int = 100
):
    db = SessionLocal()
    try:
        query = db.query(Track)
        if search:
            query = query.filter(
                or_(
                    Track.title.ilike(f"%{search}%"),
                    Track.artist.ilike(f"%{search}%"),
                    Track.album.ilike(f"%{search}%")
                )
            )
        if sort == "size_desc":
            query = query.order_by(desc(Track.file_size))
        elif sort == "size_asc":
            query = query.order_by(Track.file_size)
        else: 
            query = query.order_by(desc(Track.added_at))
            
        tracks = query.offset(skip).limit(limit).all()
        total = query.count()
        return {"total_indexados": total, "tracks": tracks}
    finally:
        db.close()

@app.get("/api/stream/{track_id}")
def stream_track(track_id: int):
    db = SessionLocal()
    track = db.query(Track).filter(Track.id == track_id).first()
    db.close()
    if not track or not os.path.exists(track.path):
        raise HTTPException(status_code=404, detail="Track not found")
    return FileResponse(track.path, media_type="audio/flac")

@app.get("/api/covers/{track_id}")
def get_cover(track_id: int):
    db = SessionLocal()
    track = db.query(Track).filter(Track.id == track_id).first()
    db.close()
    if not track or not os.path.exists(track.path):
        raise HTTPException(status_code=404, detail="Track not found")
    try:
        audio = FLAC(track.path)
        if audio.pictures:
            return Response(content=audio.pictures[0].data, media_type=audio.pictures[0].mime)
        raise HTTPException(status_code=404)
    except Exception:
        raise HTTPException(status_code=404)