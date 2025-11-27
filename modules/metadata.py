# metadata.py – Blue Tick Data™ 0.1.5
# Extracts metadata from files (MIME type, size, etc.)

import mimetypes
from pathlib import Path
import os


def extract_metadata(file_path):
	"""
	Extracts metadata from a file.
	
	Args:
		file_path: Path to the file (string or Path object)
	
	Returns:
		Dictionary containing file metadata
	"""
	path = Path(file_path)
	
	if not path.exists():
		return {
			"mime_type": "unknown",
			"size_kb": 0,
			"extension": "",
			"error": "File not found"
		}
	
	# Get MIME type
	mime_type, _ = mimetypes.guess_type(str(path))
	if mime_type is None:
		# Fallback based on extension
		ext = path.suffix.lower()
		mime_map = {
			".json": "application/json",
			".txt": "text/plain",
			".pdf": "application/pdf",
			".jpg": "image/jpeg",
			".jpeg": "image/jpeg",
			".png": "image/png",
			".gif": "image/gif",
			".mp3": "audio/mpeg",
			".wav": "audio/wav",
			".mp4": "video/mp4",
			".avi": "video/x-msvideo",
			".csv": "text/csv",
			".xml": "application/xml",
			".zip": "application/zip"
		}
		mime_type = mime_map.get(ext, "application/octet-stream")
	
	# Get file size
	size_bytes = path.stat().st_size
	size_kb = round(size_bytes / 1024, 2)
	
	# Get file extension
	extension = path.suffix
	
	# Get file timestamps
	created_at = os.path.getctime(str(path))
	modified_at = os.path.getmtime(str(path))
	
	return {
		"mime_type": mime_type,
		"size_kb": size_kb,
		"size_bytes": size_bytes,
		"extension": extension,
		"created_at": created_at,
		"modified_at": modified_at
	}