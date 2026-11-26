import os
import time
import threading
import gc
from mutagen.flac import FLAC
from sqlalchemy import delete
from .models import Track
from .database import SessionLocal

class Config:
    MUSIC_DIR = "/Volumes/M0SEAJ"
    is_scanning = False
    last_status = False

# FUNCIÓN AISLADA: Al terminar, la RAM asignada a la carátula y el FLAC se libera automáticamente.
def get_track_metadata(filepath, filename):
    try:
        audio = FLAC(filepath)
        track_num_raw = audio.get("tracknumber", ["0"])[0]
        try:
            track_num = int(str(track_num_raw).split('/')[0])
        except ValueError:
            track_num = 0

        return Track(
            filename=filename,
            title=audio.get("title", [filename])[0],
            artist=audio.get("artist", ["Desconocido"])[0],
            album=audio.get("album", ["Desconocido"])[0],
            track_number=track_num,
            duration=audio.info.length if hasattr(audio, 'info') else 0.0,
            path=filepath,
            file_size=os.path.getsize(filepath),
            bit_depth=getattr(audio.info, 'bits_per_sample', 16),
            sample_rate=getattr(audio.info, 'sample_rate', 44100),
            bitrate=getattr(audio.info, 'bitrate', 0),
            added_at=os.path.getmtime(filepath)
        )
    except Exception:
        return None

def scan_directory(force_clear=False):
    if Config.is_scanning: return
    Config.is_scanning = True
    
    db = SessionLocal()
    try:
        # Si se solicita, limpiamos la base de datos para empezar desde cero sin duplicados
        if force_clear:
            print("Limpiando biblioteca para escanear desde 0...", flush=True)
            db.execute(delete(Track))
            db.commit()

        print(f"Iniciando escaneo ultra-rápido en {Config.MUSIC_DIR}...", flush=True)
        
        tracks_to_insert = []
        count = 0
        
        # Búsqueda en memoria RAM (O(1)) para no saturar SQLite buscando duplicados
        existing_paths = {row[0] for row in db.query(Track.path).all()}

        for root, dirs, files in os.walk(Config.MUSIC_DIR):
            for file in files:
                if file.lower().endswith(".flac") and not file.startswith("."):
                    filepath = os.path.join(root, file)
                    
                    if filepath not in existing_paths:
                        track_obj = get_track_metadata(filepath, file)
                        if track_obj:
                            tracks_to_insert.append(track_obj)
                            existing_paths.add(filepath)
                            count += 1
                            
                            # INSERCIÓN MASIVA: Guarda 500 canciones a la vez (Latencia 0)
                            if len(tracks_to_insert) >= 500:
                                db.bulk_save_objects(tracks_to_insert)
                                db.commit()
                                tracks_to_insert.clear()
                                gc.collect() # Forzar limpiador de basura de RAM
                                print(f"Indexados {count} archivos...", flush=True)
        
        # Guardar el resto
        if tracks_to_insert:
            db.bulk_save_objects(tracks_to_insert)
            db.commit()
        
        print(f"Escaneo finalizado. Total agregados: {count}.", flush=True)
    except Exception as e:
        print(f"Error general en escaneo: {e}", flush=True)
        db.rollback()
    finally:
        db.close()
        gc.collect()
        Config.is_scanning = False

def monitor_usb():
    while True:
        try:
            current_status = os.path.exists(Config.MUSIC_DIR) and len(os.listdir(Config.MUSIC_DIR)) > 0
            # Si se conecta un USB de golpe, forzamos un inicio desde 0
            if current_status and not Config.last_status:
                scan_directory(force_clear=True)
            Config.last_status = current_status
        except Exception:
            pass
        time.sleep(5)