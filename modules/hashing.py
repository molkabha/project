import hashlib
from pathlib import Path

def compute_hash(file_path: Path, algorithm='sha256') -> str:
    h = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def compute_dataset_hash(file_hashes: list) -> str:
    file_hashes = [str(h) for h in file_hashes]
    payload = "dataset::" + ''.join(sorted(file_hashes))
    return hashlib.sha256(payload.encode()).hexdigest()
