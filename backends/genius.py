import logging
from typing import Optional
from backends.base import GetLyricsBase
from lyricsgenius import Genius
import re

_LOGGER = logging.getLogger(__name__)


class GetLyricsGenius(GetLyricsBase):
    """Sometimes lyrics without timestamps is better than no lyrics at all"""

    def __init__(self, args):
        super().__init__(args)
        self.name = "genius"
        self.has_timestamps = False

        if not args.genius_access_token:
            raise ValueError(
                "Genius acccess token must be provided to use the Genius backend."
            )

        self.__genius = Genius(
            args.genius_access_token,
            skip_non_songs=True,
            verbose=args.verbose,
            remove_section_headers=True,
            retries=3,
        )
        self.remove_words_from_title_artist = []

    def __scrub_lyrics(self, result_title: str, lyrics: str) -> str:
        # Remove "<title> Lyrics" header
        lyrics = re.sub(rf"^{result_title} Lyrics", "", lyrics)

        # Remove "Embed##" from the end
        lyrics = re.sub(r"[0-9]+Embed$", "", lyrics)

        return lyrics.strip()

    def get_lyrics(
        self, title_raw: str, artist_raw: str, duration_raw: int
    ) -> Optional[str]:
        title, artist, duration = self.standardise(title_raw, artist_raw, duration_raw)
        _LOGGER.debug(f"Getting lyrics for: {title} - {artist}")
        try:
            # TODO: Get multiple results in case first one isn't valid
            song = self.__genius.search_song(title, artist, get_full_info=False)
            if song and self.validate_result(title, artist, duration, song.full_title):
                _LOGGER.debug(f"Got lyrics for: {title} - {artist}")
                return self.__scrub_lyrics(song.title, song.lyrics)
            return None
        except Exception:
            _LOGGER.exception(f"Could not get lyrics for: {title} - {artist}")
            return None
