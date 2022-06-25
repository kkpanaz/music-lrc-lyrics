import logging
from backends.base import GetLyricsBase

_LOGGER = logging.getLogger(__name__)


class GetLyricsLyricsify(GetLyricsBase):
    def __init__(self, args):
        super().__init__(args)
        self.name = "lyricsify"
        self.has_timestamps = True
        self.base_url = "https://www.lyricsify.com"
        self.search_url = f"{self.base_url}/search"
        self.query_key = "q"
        self.link_strainer_args = {"name": "div", "attrs": {"class": "row ul"}}
        self.link_result_args = {"name": "a", "attrs": {"class": "title"}}
        self.lyrics_strainer_args = {"name": "div", "attrs": {"id": "entry"}}
        self.validate_duration = False  # Results don't list time
