from typing import List, Optional
from backends.megalobiz import GetLyricsMegalobiz
from backends.base import GetLyricsBase
from backends.genius import GetLyricsGenius

import logging
_LOGGER = logging.getLogger(__name__)

_BACKENDS_WITH_TIMESTAMPS = {"megalobiz": GetLyricsMegalobiz}
_BACKENDS_NO_TIMESTAMPS = {"genius": GetLyricsGenius}

# Don't include non-timestamp backends by default
# because the point of this program is to get LRC lyrics
def get_all_backends() -> List[str]:
    return list(_BACKENDS_WITH_TIMESTAMPS.keys())

def get_all_no_timestamp_backends() -> List[str]:
    return list(_BACKENDS_NO_TIMESTAMPS.keys())

def get_backend_class(backend: str) -> Optional[List[GetLyricsBase]]:
    be_lower = backend.lower()
    if be_lower in _BACKENDS_WITH_TIMESTAMPS:
        return _BACKENDS_WITH_TIMESTAMPS[be_lower]
    if be_lower in _BACKENDS_NO_TIMESTAMPS:
        return _BACKENDS_NO_TIMESTAMPS[be_lower]
    return None

def has_timestamps(backend: str) -> bool:
    return backend in _BACKENDS_WITH_TIMESTAMPS
