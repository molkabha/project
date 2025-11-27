# ingestion.py – Blue Tick Data™ 0.1.5
# Scans folder and returns file information with SHA256 hashes

import hashlib
from pathlib import Path


def compute_file_hash(file_path):
	"""
	Computes SHA256 hash of a file.
	"""
	sha256_hash = hashlib.sha256()
	
	with open(file_path, "rb") as f:
		# Read file in chunks to handle large files
		for byte_block in iter(lambda: f.read(4096), b""):
			sha256_hash.update(byte_block)
	
	return sha256_hash.hexdigest()


def scan_folder(folder_path):
	"""
	Recursively scans a folder and returns list of file dictionaries.
	Each dictionary contains: path, filename, and sha256 hash.
	"""
	folder = Path(folder_path)
	
	if not folder.exists():
		raise ValueError(f"Folder does not exist: {folder_path}")
	
	if not folder.is_dir():
		raise ValueError(f"Path is not a directory: {folder_path}")
	
	files = []
	
	# Recursively find all files
	for file_path in folder.rglob("*"):
		if file_path.is_file():
			try:
				file_hash = compute_file_hash(file_path)
				
				files.append({
					"path": str(file_path),
					"filename": file_path.name,
					"sha256": file_hash
				})
				
				print(f"✓ Scanned: {file_path.name}")
				
			except Exception as e:
				print(f"✗ Error scanning {file_path.name}: {e}")
				continue
	
	print(f"\n✓ Total files scanned: {len(files)}")
	return files