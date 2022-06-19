from backends.megalobiz import GetLyricsMegalobiz

_BACKENDS = {"megalobiz": GetLyricsMegalobiz}

def get_all_backends():
    return _BACKENDS.keys()

def get_backend_class(backend: str):
    if backend.lower() in _BACKENDS:
        return _BACKENDS[backend]
    return None
