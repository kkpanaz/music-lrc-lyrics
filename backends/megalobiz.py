import logging
from backends.base import GetLyricsBase
import re

_LOGGER = logging.getLogger(__name__)


class GetLyricsMegalobiz(GetLyricsBase):
    def __init__(self, args):
        super().__init__(args)
        self.name = "megalobiz"
        self.has_timestamps = True
        self.base_url = "https://www.megalobiz.com"
        self.search_url = f"{self.base_url}/search/all"
        self.query_key = "qry"
        self.link_strainer_args = {
            "name": "div",
            "attrs": {"id": "list_entity_container"},
        }
        self.link_result_args = {"name": "a", "attrs": {"class": "entity_name"}}
        self.lyrics_strainer_args = {
            "name": "span",
            "attrs": {"id": re.compile(r"lrc_[0-9]+_lyrics")},
        }
