from typing import List, Optional
from backends.megalobiz import GetLyricsMegalobiz
from backends.base import GetLyricsBase

_BACKENDS = {"megalobiz": GetLyricsMegalobiz}

def get_all_backends() -> List[str]:
    return _BACKENDS.keys()

def get_backend_class(backend: str) -> Optional[List[GetLyricsBase]]:
    if backend.lower() in _BACKENDS:
        return _BACKENDS[backend]
    return None
