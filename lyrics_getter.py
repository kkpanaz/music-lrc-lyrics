import math
from pathlib import Path
import re
from backends.base import GetLyricsBase

import logging
from typing import List, Tuple

_LOGGER = logging.getLogger(__name__)

class LyricsGetter:
    def __init__(self, backends: List[GetLyricsBase], input_path: Path, output_root: Path, separator: str):
        self.__backends = backends
        self.__input_path = input_path
        self.__output_root = output_root
        self.__separator = separator
        self.__failed_path = output_root / "failed.txt"

        with open(self.__failed_path, 'w'):
            # Clear failed file
            pass

    def __import_spotify_playlist(self) -> List[Tuple[str, str, int]]:
        with open(self.__input_path) as file:
            data = []
            for line in file.readlines():
                artist, title, time_str = line.split(self.__separator)
                hours, mins, secs = re.findall(r'(\d{2}):(\d{2}):(\d{2})', time_str.strip())[0]
                time_secs = int(hours)*3600 + int(mins)*60 + int(secs)
                data.append((title.strip(), artist.strip(), time_secs))
        return data

    def __get_output_file_path(self, title: str, artist: str) -> Path:
        return self.__output_root/artist/f"{title}.lrc"

    def __save_lyrics_file(self, title: str, artist: str, lyrics: str) -> None:
        output = self.__get_output_file_path(title, artist)
        output.parent.mkdir(exist_ok=True)
        with open(output, 'w') as file:
            file.write(lyrics)

    def __save_song_as_failed(self, title: str, artist: str, duration: int) -> None:
        hours = math.floor(duration / 3600)
        duration -= hours * 3600
        mins = math.floor(duration / 60)
        duration -= mins * 60
        with open(self.__failed_path, 'a') as file:
            data = self.__separator.join([artist, title, f"{hours:02d}:{mins:02d}:{duration:02d}"])
            file.write(f"{data}\n")

    def run(self) -> None:
        data = self.__import_spotify_playlist()
        num_skipped = 0
        num_saved = 0
        num_failed = 0
        _LOGGER.info(f"Getting lyrics for {len(data)} songs")
        for title, artist, duration in data:
            lyric_file = self.__get_output_file_path(title, artist)
            if lyric_file.exists():
                _LOGGER.debug(f"Skipping lyrics that exist: {title} - {artist}")
                num_skipped += 1
                continue

            lyrics = None
            for backend in self.__backends:
                lyrics = backend.get_lyrics(title, artist, duration)
                if lyrics:
                    break
            if lyrics:
                self.__save_lyrics_file(title, artist, lyrics)
                num_saved += 1
                _LOGGER.debug(f"Successfully got lyrics for: {title} - {artist}")
            else:
                self.__save_song_as_failed(title, artist, duration)
                num_failed += 1
                _LOGGER.debug(f"Failed to get lyrics for: {title} - {artist}")
        _LOGGER.info(f"Finished getting lyrics: Skipped={num_skipped} Saved={num_saved} Failed={num_failed}")