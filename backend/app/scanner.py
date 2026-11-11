import os
from mutagen.flac import FLAC
from .models import Track
from .database import SessionLocal

MUSIC_DIR = os.getenv("MUSIC_DIR", "/music")

def scan_directory():
    print("Iniciando escaneo rápido de directorio...", flush=True)
    db = SessionLocal()
    try:
        count = 0
        batch_size = 200 
        
        for root, dirs, files in os.walk(MUSIC_DIR):
            for file in files:
                if file.lower().endswith(".flac") and not file.startswith("."):
                    filepath = os.path.join(root, file)
                    if not db.query(Track).filter(Track.path == filepath).first():
                        try:
                            audio = FLAC(filepath)
                            
                            # Extraer número de pista real (FLAC suele guardarlo como "1" o "01/12")
                            track_num_raw = audio.get("tracknumber", ["0"])[0]
                            try:
                                track_num = int(str(track_num_raw).split('/')[0])
                            except ValueError:
                                track_num = 0

                            track = Track(
                                filename=file,
                                title=audio.get("title", [file])[0],
                                artist=audio.get("artist", ["Desconocido"])[0],
                                album=audio.get("album", ["Desconocido"])[0],
                                track_number=track_num, # Guardamos el orden
                                duration=audio.info.length if hasattr(audio, 'info') else 0.0,
                                path=filepath,
                                file_size=os.path.getsize(filepath),
                                bit_depth=getattr(audio.info, 'bits_per_sample', 16),
                                sample_rate=getattr(audio.info, 'sample_rate', 44100),
                                bitrate=getattr(audio.info, 'bitrate', 0),
                                added_at=os.path.getmtime(filepath)
                            )
                            db.add(track)
                            count += 1
                            
                            if count % batch_size == 0:
                                db.commit()
                                print(f"Indexados {count} archivos...", flush=True)
                        except Exception as e:
                            print(f"Error procesando {file}: {e}", flush=True)
        
        db.commit()
        print("Escaneo finalizado exitosamente.", flush=True)
    finally:
        db.close()