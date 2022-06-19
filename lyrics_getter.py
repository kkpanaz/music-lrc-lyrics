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
                parts = line.split(self.__separator)
                if len(parts) != 3:
                    _LOGGER.warning(f"Skipping input line {line}. Should be <artist>{self.__separator}<title>{self.__separator}HH:MM:SS")
                    continue
                artist, title, time = line.split(self.__separator)
                data.append((title.strip(), artist.strip(), time.strip()))
        return data

    def __get_output_file_path(self, title: str, artist: str) -> Path:
        return self.__output_root/artist/f"{title}.lrc"

    def __save_lyrics_file(self, title: str, artist: str, lyrics: str) -> None:
        output = self.__get_output_file_path(title, artist)
        output.parent.mkdir(exist_ok=True)
        try:
            with open(output, 'w') as file:
                file.write(lyrics)
        except Exception:
            _LOGGER.exception(f"Cannot write lyrics of {title} - {artist} to {output}")

    def __save_song_as_failed(self, title: str, artist: str, duration: int) -> None:
        with open(self.__failed_path, 'a') as file:
            data = self.__separator.join([artist, title, duration])
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
                uniform_title, uniform_artist, uniform_duration = backend.uniformise(title, artist, duration)
                if not uniform_title or not uniform_artist or not uniform_duration:
                    _LOGGER.debug(f"Failed to uniformise: {title} - {artist} using backend {backend.name}")
                    continue
                lyrics = backend.get_lyrics(uniform_title, uniform_artist, uniform_duration)
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