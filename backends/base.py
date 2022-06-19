import requests
import logging


_LOGGER = logging.getLogger(__name__)

class GetLyricsBase:
    def __init__(self):
        self.session = requests.Session()
        self.durantion_padding = 5

    def get_lyrics(self, title, artist, duration_secs):
        raise NotImplementedError