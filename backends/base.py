from typing import Optional, Tuple
import requests
import logging
import re


_LOGGER = logging.getLogger(__name__)

class GetLyricsBase:
    def __init__(self):
        self.name = "base"
        self.session = requests.Session()
        self.durantion_padding = 5
        self.ignore_keywords_in_title_brackets = ["feat", "acoustic", "bonus", "from", "version", "cover", "live", "remix", "theme", "official"]
        self.remove_words_from_title_artist = ["a", "the", "of"]

    def get_lyrics(self, title: str, artist: str, duration_secs: int) -> Optional[str]:
        raise NotImplementedError

    def __remove_punctuation(self, string: str) -> str:
        string = re.sub(r"[’`'\"]", "", string)
        string = re.sub(r"[^A-Za-z0-9]", " ", string)
        string = re.sub(r"-", " ", string)
        string_parts = string.split()
        string_parts = [part for part in string_parts if part not in self.remove_words_from_title_artist]
        string = " ".join(string_parts)
        return string

    def __uniformise_title(self, title: str) -> str:
        title = title.strip().lower()
        brackets = re.findall('\(.*?\)', title)
        for bracket in brackets:
            if any([keyword in bracket for keyword in self.ignore_keywords_in_title_brackets]):
                title = title.replace(bracket, "")
        title = self.__remove_punctuation(title)
        return title

    def __uniformise_artist(self, artist: str) -> str:
        artist = artist.strip().lower()
        if ";" in artist: # Remove multiple artists
            artist = artist.split(";")[0].strip()

        artist = self.__remove_punctuation(artist)
        return artist

    def __get_secs_from_time_str(self, time: str) -> Optional[int]:
        time = time.strip()
        time_parts = re.findall(r'^(\d{2}):(\d{2}):(\d{2})$', time)
        if not time_parts or len(time_parts) != 1:
            _LOGGER.debug(f"Failed to uniformise: {time} does not match HH:MM:SS")
            return None
        hours, mins, secs = time_parts[0]
        return int(hours)*3600 + int(mins)*60 + int(secs)

    def uniformise(self, title: str, artist: str, duration: str) -> Tuple[str, str, Optional[int]]:
        title = self.__uniformise_title(title)
        artist = self.__uniformise_artist(artist)
        dur_secs = self.__get_secs_from_time_str(duration)
        return title, artist, dur_secs