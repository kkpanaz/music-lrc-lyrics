from typing import Optional, Tuple
import requests
import logging
import re
from bs4 import BeautifulSoup, SoupStrainer

# For Beautiful Soup speed
import lxml
import cchardet


_LOGGER = logging.getLogger(__name__)


class GetLyricsBase:
    def __init__(self, args):
        ### BASIC SETUP ###
        self.session = requests.Session()
        self.request_headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
        }
        self.duration_padding = 5
        self.time_regex = r"\[(\d{2}):(\d{2}.\d{2})\]"
        self.ignore_keywords_in_title_brackets = [
            "feat",
            "acoustic",
            "bonus",
            "from",
            "version",
            "cover",
            "live",
            "remix",
            "theme",
            "official",
            "explicit",
        ]
        self.remove_words_from_title_artist = ["a", "the", "of"]

        ### IMPLEMENTATION SHOULD OVERRIDE ###
        self.name = "base"
        self.has_timestamps = False
        self.base_url = None
        self.search_url = None
        self.query_key = None

        # Does link result include the base URL?
        self.link_includes_base = False
        # Does the results include a duration?
        self.validate_duration = True

        # The following 3 arguments should follow the format:
        # {"name": "div", "attrs": {"class": "row ui"}}
        # See https://www.crummy.com/software/BeautifulSoup/bs4/doc/#kinds-of-filters

        # HTML tag containing all the results
        self.link_strainer_args = None
        # HTML tag containing a single result (should have href attribute)
        self.link_result_args = None
        # HTML tag containing the lyrics text
        self.lyrics_strainer_args = None

    ### CALL THIS FUNCTION ###

    def get_lyrics(
        self, title_raw: str, artist_raw: str, duration_raw: str
    ) -> Optional[str]:
        assert self.lyrics_strainer_args
        title, artist, duration = self.standardise(title_raw, artist_raw, duration_raw)
        if not duration and self.validate_duration:
            return None
        _LOGGER.debug(f"{self.name}: Getting lyrics for: {title} - {artist}")
        link = self.get_link(title, artist, duration)
        if not link:
            return None
        if not self.link_includes_base:
            link = f"{self.base_url}{link}"
        try:
            response = self.session.get(
                url=link,
                headers=self.request_headers,
            )
            response.raise_for_status()
            strainer = SoupStrainer(**self.lyrics_strainer_args)
            result = BeautifulSoup(response.text, "lxml", parse_only=strainer)
            lyrics = result.get_text(separator="\n", strip=True)
            _LOGGER.debug(f"{self.name}: Got lyrics for: {title} - {artist}")
            return self.scrub_lyrics(lyrics)
        except Exception as ex:
            _LOGGER.debug(f"{self.name}: Could not get lyrics from link: {link}: {ex}")
            return None

    ### HELPER FUNCTIONS (FOR IMPLEMENTATIONS TO OVERRIDE) ###

    def get_link(
        self, title: str, artist: str, duration_secs: Optional[int]
    ) -> Optional[str]:
        assert self.base_url and self.search_url and self.query_key
        assert self.link_strainer_args and self.link_result_args
        _LOGGER.debug(f"{self.name}: Getting link for: {title} - {artist}")
        duration = duration_secs if self.validate_duration else None
        params = "+".join(title.split() + artist.split())
        try:
            response = self.session.get(
                url=self.search_url,
                params={self.query_key: params},
                headers=self.request_headers,
            )
            response.raise_for_status()
            strainer = SoupStrainer(**self.link_strainer_args)
            parsed_html = BeautifulSoup(response.text, "lxml", parse_only=strainer)
            results = parsed_html.find_all(**self.link_result_args)
            for result in results:
                result_text = result.text.strip().lower()
                if self.validate_result(title, artist, duration, result_text):
                    link = result.get_attribute_list(key="href")[0]
                    _LOGGER.debug(
                        f"{self.name}: Got link for: {title} - {artist}: {link}"
                    )
                    return link
            _LOGGER.debug(
                f"{self.name}: Failed to get valid link for {title} - {artist} from {len(results)} results"
            )
            return None
        except Exception as ex:
            _LOGGER.debug(
                f"{self.name}: Could not get link to lyrics from search result: {self.query_key}?={params}: {ex}"
            )
            return None

    def scrub_lyrics(self, lyrics: str) -> str:
        # Nothing to scrub by default
        return lyrics

    def remove_punctuation(self, string: str) -> str:
        string = re.sub(r"[’`'\"]", "", string)
        string = re.sub(r"[^A-Za-z0-9]", " ", string)
        string = re.sub(r"-", " ", string)
        string_parts = string.split()
        string_parts = [
            part
            for part in string_parts
            if part not in self.remove_words_from_title_artist
        ]
        string = " ".join(string_parts)
        return string

    def standardise_title(self, title: str) -> str:
        title = title.strip().lower()
        brackets = re.findall("\(.*?\)", title)
        brackets += re.findall("\[.*?\]", title)
        for bracket in brackets:
            if any(
                [
                    keyword in bracket
                    for keyword in self.ignore_keywords_in_title_brackets
                ]
            ):
                title = title.replace(bracket, "")
        title = self.remove_punctuation(title)
        return title

    def standardise_artist(self, artist: str) -> str:
        artist = artist.strip().lower()
        if ";" in artist:  # Remove multiple artists
            artist = artist.split(";")[0].strip()

        artist = self.remove_punctuation(artist)
        return artist

    def get_secs_from_time_str(self, duration: str) -> Optional[int]:
        duration = duration.strip()
        duration_parts = re.findall(r"^(\d{2}):(\d{2}):(\d{2})$", duration)
        if not duration_parts or len(duration_parts) != 1:
            _LOGGER.debug(
                f"{self.name}: Failed to standardise: {duration} does not match HH:MM:SS"
            )
            return None
        hours, mins, secs = duration_parts[0]
        return int(hours) * 3600 + int(mins) * 60 + int(secs)

    def standardise(
        self, title: str, artist: str, duration: str
    ) -> Tuple[str, str, Optional[int]]:
        title = self.standardise_title(title)
        artist = self.standardise_artist(artist)
        dur_secs = self.get_secs_from_time_str(duration)
        return title, artist, dur_secs

    def validate_result(
        self, title: str, artist: str, duration_secs: Optional[int], result_str: str
    ) -> bool:
        # Validate title and artist
        parts = title.split() + artist.split()
        if not all([part.lower() in result_str.lower() for part in parts]):
            _LOGGER.debug(
                f"{self.name}: Invalid result for: {title} - {artist}: {result_str} failed: No matching title and artist"
            )
            return False

        # Duration doesn't need to be validated if lyrics don't have timestamps
        if not self.has_timestamps or not duration_secs:
            return True

        # Validate duration
        time_match = re.findall(rf".*{self.time_regex}", result_str)
        if not time_match:
            _LOGGER.debug(
                f"{self.name}: Invalid result for: {title} - {artist}: {result_str} failed: No valid time stamp"
            )
            return False
        mins, secs = time_match[-1]
        time_secs = int(mins) * 60 + float(secs)
        valid_time = abs(time_secs - duration_secs) <= self.duration_padding
        if not valid_time:
            _LOGGER.debug(
                f"{self.name}: Invalid result for: {title} - {artist}: {result_str} failed: Out of time range (padding={self.duration_padding})"
            )
            return False
        return True
