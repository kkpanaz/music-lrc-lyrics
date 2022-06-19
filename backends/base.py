from typing import Optional
import requests
import logging


_LOGGER = logging.getLogger(__name__)

class GetLyricsBase:
    def __init__(self):
        self.session = requests.Session()
        self.durantion_padding = 5

    def get_lyrics(self, title: str, artist: str, duration_secs: int) -> Optional[str]:
        raise NotImplementedError