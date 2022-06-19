from pathlib import Path
import re
import requests
from bs4 import BeautifulSoup
import lxml
import cchardet

import logging


_LOGGER = logging.getLogger(__name__)

class LyricsGetter:
    def __init__(self):
        self.__base_url = "https://www.megalobiz.com"
        self.__search_url = f"{self.__base_url}/search/all"
        self.__query_key = "qry"
        self.__session = requests.Session()
        self.__durantion_padding = 5
        self.__input_path = None
        self.__output_root = None
        self.__separator = None
    
    def __get_link(self, title: str, artist: str, duration_secs: float):
        params = f"{title}+{artist}".replace(" ", "+")
        try:
            response = self.__session.get(url=self.__search_url, params={self.__query_key: params})
            response.raise_for_status()
            parsed_html = BeautifulSoup(response.text, features="lxml")
            results = parsed_html.body.find_all('a', attrs={'class':'entity_name'})
            for result in results:
                result_text = result.text.strip()
                if title not in result_text or artist not in result_text:
                    continue
                time_match = re.findall(r'.*\[(\d{2}):(\d{2}.\d{2})\]', result_text)
                if not time_match:
                    continue
                mins, secs = time_match[0]
                time_secs = int(mins)*60 + float(secs)
                valid_time = abs(time_secs - duration_secs) <= self.__durantion_padding
                if not valid_time:
                    continue
                return result.get_attribute_list(key="href")[0]
        except Exception:
            _LOGGER.exception(f'Could not get link to lyrics from search result: {self.__query_key}={params}')
            return None
        
        _LOGGER.warning(f"Failed to get valid result for {title} - {artist}")
        return None

    def get_lyrics(self, title, artist, duration_secs):
        link = self.__get_link(title, artist, duration_secs)
        if not link:
            return None
        url = f"{self.__base_url}{link}"
        try:
            response = self.__session.get(url=url)
            response.raise_for_status()
            parsed_html = BeautifulSoup(response.text, features="lxml")
            lyrics = parsed_html.body.find('div', attrs={'class':'lyrics_details entity_more_info'}).find('span').get_text()
            return lyrics
        except Exception:
            _LOGGER.exception(f'Could not get lyrics from link: {url}')
            return None

    def import_spotify_playlist(self, file_path, separator):
        with open(file_path) as file:
            data = []
            for line in file.readlines():
                artist, title, time_str = line.split(separator)
                hours, mins, secs = re.findall(r'(\d{2}):(\d{2}):(\d{2})', time_str.strip())[0]
                time_secs = int(hours)*3600 + int(mins)*60 + int(secs)
                data.append((title.strip(), artist.strip(), time_secs))
            return data

    def get_output_file_path(self, title, artist, root):
        return root/artist/f"{title}.lrc"

    def lyrics_to_file(self, title, artist, lyrics, root):
        output = self.get_output_file_path(title, artist, root)
        output.parent.mkdir(exist_ok=True)
        with open(output, 'w') as file:
            file.write(lyrics)

    def run(self, input_path, output_root, separator="|"):
        self.__input_path = input_path
        self.__output_root = output_root
        self.__separator = separator

        data = self.import_spotify_playlist(input_path, separator)
        for title, artist, duration in data:
            lyric_file = self.get_output_file_path(title, artist, output_root)
            if lyric_file.exists():
                _LOGGER.debug(f"Skippings lyrics that exist: {title} - {artist}")
                continue

            lyrics = self.get_lyrics(title, artist, duration)
            if lyrics:
                self.lyrics_to_file(title, artist, lyrics, output_root)
                _LOGGER.debug(f"Successfully got lyrics for: {title} - {artist}")


def main():
    lg = LyricsGetter()
    lg.run(Path.cwd()/"data"/"twhbc-20220613.txt",  Path.cwd()/"lyrics")

if __name__ == "__main__":
    main()