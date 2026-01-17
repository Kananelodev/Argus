import hashlib
from pathlib import Path
from typing import Union

class ModelHasher:
    @staticmethod
    def hash_file(file_path: Union[str, Path], chunk_size: int = 8192) -> str:
        """
        Generates a SHA-256 hash of a file efficiently by reading in chunks.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            while chunk := f.read(chunk_size):
                sha256.update(chunk)
        
        return sha256.hexdigest()

    @staticmethod
    def hash_string(content: str) -> str:
        """
        Generates a SHA-256 hash of a string input.
        """
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
