from fastapi import FastAPI, BackgroundTasks, Depends, Query, Response, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading, os
from mutagen.flac import FLAC
from pydantic import BaseModel

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from .database import engine, Base, get_db
from .models import Track
from .scanner import scan_directory, monitor_usb, Config

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=monitor_usb, daemon=True).start()
    threading.Thread(target=scan_directory, daemon=True).start()
    yield

app = FastAPI(title="FLAC Player API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

class PathUpdate(BaseModel):
    path: str

@app.post("/api/settings/path")
def update_path(data: PathUpdate, background_tasks: BackgroundTasks):
    Config.MUSIC_DIR = data.path
    Config.last_status = False
    # Escanear desde 0 al guardar nueva ruta
    background_tasks.add_task(scan_directory, force_clear=True)
    return {"status": "ok", "path": Config.MUSIC_DIR}

@app.post("/api/scan")
def trigger_scan(background_tasks: BackgroundTasks):
    # El botón "Sincronizar" ahora limpia duplicados y empieza de 0
    background_tasks.add_task(scan_directory, force_clear=True)
    return {"status": "ok"}
  
@app.get("/api/status")
def get_device_status():
    try:
        is_mounted = os.path.exists(Config.MUSIC_DIR) and len(os.listdir(Config.MUSIC_DIR)) > 0
        return {"connected": is_mounted, "path": Config.MUSIC_DIR}
    except Exception:
        return {"connected": False, "path": Config.MUSIC_DIR}

@app.get("/api/info")
def get_library_info(db: Session = Depends(get_db)):
    total = db.query(Track).count()
    return {"library_path": MUSIC_DIR, "total_tracks": total}

@app.get("/api/tracks")
def get_tracks(
    search: str = None, album: str = None, artist: str = None,
    page: int = Query(1, ge=1), limit: int = Query(24, ge=1, le=100),
    db: Session = Depends(get_db)
):
    query = db.query(Track)
    if search: 
        query = query.filter(or_(Track.title.ilike(f"%{search}%"), Track.artist.ilike(f"%{search}%"), Track.album.ilike(f"%{search}%")))
    
    if artist: query = query.filter(Track.artist == artist)
        
    if album: 
        query = query.filter(Track.album == album)
        # ORDENAMOS POR EL NÚMERO REAL DEL DISCO
        query = query.order_by(Track.track_number.asc())
    else:
        query = query.order_by(desc(Track.added_at))
    
    total = query.count()
    total_pages = (total + limit - 1) // limit
    tracks = query.offset((page - 1) * limit).limit(limit).all()
    
    return {"tracks": tracks, "total": total, "page": page, "total_pages": total_pages}

@app.get("/api/albums")
def get_albums(db: Session = Depends(get_db)):
    # Corrección para que la barra lateral reciba correctamente el ID de la primera canción y muestre la foto
    albums = db.query(Track.album, func.min(Track.id)).filter(Track.album != None).group_by(Track.album).all()
    return [{"name": a[0], "id": a[1]} for a in albums if a[0]]

@app.get("/api/artists")
def get_artists(db: Session = Depends(get_db)):
    return [a[0] for a in db.query(Track.artist).distinct().all()]

@app.get("/api/stream/{track_id}")
def stream_track(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track or not os.path.exists(track.path): raise HTTPException(404)
    return FileResponse(track.path, media_type="audio/flac")

@app.get("/api/covers/{track_id}")
def get_cover(track_id: int, db: Session = Depends(get_db)):
    track = db.query(Track).filter(Track.id == track_id).first()
    if not track or not os.path.exists(track.path): raise HTTPException(404)
    try:
        audio = FLAC(track.path)
        if audio.pictures: return Response(content=audio.pictures[0].data, media_type=audio.pictures[0].mime)
        raise HTTPException(404)
    except:
        raise HTTPException(404)
      
@app.get("/api/directories")
def list_directories(path: str = "/Volumes"):
    try:
        # Asegurar que la ruta exista
        if not os.path.exists(path) or not os.path.isdir(path):
            return {"directories": [], "current_path": path}
        
        # Listar solo carpetas (ignorando archivos ocultos)
        dirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d)) and not d.startswith('.')]
        return {"directories": sorted(dirs), "current_path": path}
    except Exception as e:
        return {"directories": [], "current_path": path, "error": str(e)}