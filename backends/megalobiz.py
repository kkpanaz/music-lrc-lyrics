import logging
from typing import Optional
from backends.base import GetLyricsBase
from bs4 import BeautifulSoup
import re

_LOGGER = logging.getLogger(__name__)

class GetLyricsMegalobiz(GetLyricsBase):
    def __init__(self, args):
        super().__init__(args)
        self.name = "megalobiz"
        self.has_timestamps = True
        self.__base_url = "https://www.megalobiz.com"
        self.__search_url = f"{self.__base_url}/search/all"
        self.__query_key = "qry"

    def __get_link(self, title: str, artist: str, duration_secs: float) -> Optional[str]:
        _LOGGER.debug(f"Getting link for: {title} - {artist}")
        params = "+".join(title.split() + artist.split())
        try:
            response = self.session.get(url=self.__search_url, params={self.__query_key: params})
            response.raise_for_status()
            parsed_html = BeautifulSoup(response.text, features="lxml")
            results = parsed_html.body.find_all('a', attrs={'class':'entity_name'})
            for result in results:
                result_text = result.text.strip().lower()
                if not self.validate_result(title, artist, duration_secs, result_text):
                    continue
                link = result.get_attribute_list(key="href")[0]
                _LOGGER.debug(f"Got link for: {title} - {artist}: {link}")
                return link
        except Exception:
            _LOGGER.exception(f'Could not get link to lyrics from search result: {self.__query_key}={params}')
            return None
    
        _LOGGER.debug(f"Failed to get valid link for {title} - {artist}")
        return None

    def get_lyrics(self, title_raw: str, artist_raw: str, duration_raw: int) -> Optional[str]:
        title, artist, duration = self.standardise(title_raw, artist_raw, duration_raw)
        _LOGGER.debug(f"Getting lyrics for: {title} - {artist}")
        link = self.__get_link(title, artist, duration)
        if not link:
            return None
        url = f"{self.__base_url}{link}"
        try:
            response = self.session.get(url=url)
            response.raise_for_status()
            parsed_html = BeautifulSoup(response.text, features="lxml")
            lyrics = parsed_html.body.find('div', attrs={'class':'lyrics_details entity_more_info'}).find('span').get_text()
            _LOGGER.debug(f"Got lyrics for: {title} - {artist}")
            return lyrics
        except Exception:
            _LOGGER.exception(f'Could not get lyrics from link: {url}')
            return None
