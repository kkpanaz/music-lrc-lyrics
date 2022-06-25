import logging
import re
from typing import Optional
from backends.base import GetLyricsBase
from bs4 import BeautifulSoup, SoupStrainer
import lxml
import cchardet

_LOGGER = logging.getLogger(__name__)


class GetLyricsRCLyricsBand(GetLyricsBase):
    def __init__(self, args):
        super().__init__(args)
        self.name = "rclyricsband"
        self.has_timestamps = True
        self.__base_url = "https://rclyricsband.com"
        self.__search_url = self.__base_url
        self.__query_key = "s"

    def __get_link(
        self, title: str, artist: str, duration_secs: float
    ) -> Optional[str]:
        _LOGGER.debug(f"Getting link for: {title} - {artist}")
        params = "+".join(title.split() + artist.split())
        try:
            response = self.session.get(
                url=self.__search_url, params={self.__query_key: params}
            )
            response.raise_for_status()
            strainer = SoupStrainer("div", attrs={"id": "content"})
            results = BeautifulSoup(response.text, "lxml", parse_only=strainer)
            for result in results.find_all("a"):
                result_text = result.text.strip().lower()
                if not self.validate_result(title, artist, duration_secs, result_text):
                    continue
                link = result.get_attribute_list(key="href")[0]
                _LOGGER.debug(f"Got link for: {title} - {artist}: {link}")
                return link
        except Exception:
            _LOGGER.exception(
                f"Could not get link to lyrics from search result: {self.__query_key}={params}"
            )
            return None

        _LOGGER.debug(f"Failed to get valid link for {title} - {artist}")
        return None

    def __scrub_lyrics(self, lyrics: str) -> str:
        lines = lyrics.split("\n")

        # Split first line of lyrics from information
        indexes = [pos for pos, char in enumerate(lines[0]) if char == "["]
        first_line_index = indexes[-2]
        info = lines[0][:first_line_index]
        first_line = lines[0][first_line_index:]
        lines[0] = first_line

        for count, line in enumerate(lines):
            # Remove extra website labels
            lines[count] = line.replace("[re:www.rclyricsband.com]", "")

            # Remove second time stamp (to match other backends)
            # Happy to remove if others want this second timestamp
            second_timestamp = lines[count][10:20]
            if re.match(rf"^{self.time_regex}$", second_timestamp):
                lines[count] = lines[count].replace(second_timestamp, "")

        # Add back in info sections split into new lines
        info_indexes = indexes[1:-2]
        for index in info_indexes[::-1]:
            lines.insert(0, info[index:])
            info = info[:index]

        return "\n".join(lines)

    def get_lyrics(
        self, title_raw: str, artist_raw: str, duration_raw: int
    ) -> Optional[str]:
        title, artist, duration = self.standardise(title_raw, artist_raw, duration_raw)
        _LOGGER.debug(f"Getting lyrics for: {title} - {artist}")
        link = self.__get_link(title, artist, duration)
        if not link:
            return None
        try:
            response = self.session.get(url=link)
            response.raise_for_status()
            strainer = SoupStrainer(
                "div", attrs={"class": "su-box-content su-u-clearfix su-u-trim"}
            )
            result = BeautifulSoup(response.text, "lxml", parse_only=strainer)
            lyrics = result.get_text(separator="\n", strip=False)
            _LOGGER.debug(f"Got lyrics for: {title} - {artist}")
            return self.__scrub_lyrics(lyrics)
        except Exception:
            _LOGGER.exception(f"Could not get lyrics from link: {link}")
            return None
