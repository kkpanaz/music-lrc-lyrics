from typing import Optional, Tuple
import requests
import logging
import re


_LOGGER = logging.getLogger(__name__)

class GetLyricsBase:
    def __init__(self, args):
        self.name = "base"
        self.has_timestamps = False
        self.session = requests.Session()
        self.duration_padding = 5
        self.ignore_keywords_in_title_brackets = ["feat", "acoustic", "bonus", "from", "version", "cover", "live", "remix", "theme", "official", "explicit"]
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

    def __standardise_title(self, title: str) -> str:
        title = title.strip().lower()
        brackets = re.findall('\(.*?\)', title)
        brackets += re.findall('\[.*?\]', title)
        for bracket in brackets:
            if any([keyword in bracket for keyword in self.ignore_keywords_in_title_brackets]):
                title = title.replace(bracket, "")
        title = self.__remove_punctuation(title)
        return title

    def __standardise_artist(self, artist: str) -> str:
        artist = artist.strip().lower()
        if ";" in artist: # Remove multiple artists
            artist = artist.split(";")[0].strip()

        artist = self.__remove_punctuation(artist)
        return artist

    def __get_secs_from_time_str(self, duration: str) -> Optional[int]:
        duration = duration.strip()
        duration_parts = re.findall(r'^(\d{2}):(\d{2}):(\d{2})$', duration)
        if not duration_parts or len(duration_parts) != 1:
            _LOGGER.debug(f"Failed to standardise: {duration} does not match HH:MM:SS")
            return None
        hours, mins, secs = duration_parts[0]
        return int(hours)*3600 + int(mins)*60 + int(secs)

    def standardise(self, title: str, artist: str, duration: str) -> Tuple[str, str, Optional[int]]:
        title = self.__standardise_title(title)
        artist = self.__standardise_artist(artist)
        dur_secs = self.__get_secs_from_time_str(duration)
        return title, artist, dur_secs

    def validate_result(self, title: str, artist: str, duration_secs: int, result_str: str) -> bool:
        # Validate title and artist
        parts = title.split() + artist.split()
        if not all([part.lower() in result_str.lower() for part in parts]):
            _LOGGER.debug(f"Invalid result for: {title} - {artist}: {result_str} failed: No matching title and artist")
            return False

        # Duration doesn't need to be validated if lyrics don't have timestamps
        if not self.has_timestamps:
            return True
        
        # Validate duration
        time_match = re.findall(r'.*\[(\d{2}):(\d{2}.\d{2})\]', result_str)
        if not time_match:
            _LOGGER.debug(f"Invalid result for: {title} - {artist}: {result_str} failed: No valid time stamp")
            return False
        mins, secs = time_match[-1]
        time_secs = int(mins)*60 + float(secs)
        valid_time = abs(time_secs - duration_secs) <= self.duration_padding
        if not valid_time:
            _LOGGER.debug(f"Invalid result for: {title} - {artist}: {result_str} failed: Out of time range (padding={self.duration_padding})")
            return False
        return True