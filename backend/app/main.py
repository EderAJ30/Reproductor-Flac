from fastapi import FastAPI, BackgroundTasks, Depends, Query, Response, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import threading, os
from mutagen.flac import FLAC

from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from .database import engine, Base, get_db
from .models import Track
from .scanner import scan_directory, MUSIC_DIR

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    threading.Thread(target=scan_directory).start()
    yield

app = FastAPI(title="FLAC Player API", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/api/scan")
def trigger_scan(background_tasks: BackgroundTasks):
    background_tasks.add_task(scan_directory)
    return {"status": "ok"}
  
@app.get("/api/status")
def get_device_status():
    try:
        is_mounted = os.path.exists(MUSIC_DIR) and len(os.listdir(MUSIC_DIR)) > 0
        return {"connected": is_mounted, "path": MUSIC_DIR}
    except Exception:
        return {"connected": False, "path": MUSIC_DIR}

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