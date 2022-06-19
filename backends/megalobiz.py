import logging
from typing import Optional
from backends.base import GetLyricsBase
from bs4 import BeautifulSoup
import re

_LOGGER = logging.getLogger(__name__)

class GetLyricsMegalobiz(GetLyricsBase):
    def __init__(self):
        super().__init__()
        self.__base_url = "https://www.megalobiz.com"
        self.__search_url = f"{self.__base_url}/search/all"
        self.__query_key = "qry"

    def __get_link(self, title: str, artist: str, duration_secs: float) -> Optional[str]:
        params = f"{title}+{artist}".replace(" ", "+")
        try:
            response = self.session.get(url=self.__search_url, params={self.__query_key: params})
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
                valid_time = abs(time_secs - duration_secs) <= self.durantion_padding
                if not valid_time:
                    continue
                return result.get_attribute_list(key="href")[0]
        except Exception:
            _LOGGER.exception(f'Could not get link to lyrics from search result: {self.__query_key}={params}')
            return None
    
        _LOGGER.warning(f"Failed to get valid result for {title} - {artist}")
        return None

    def get_lyrics(self, title: str, artist: str, duration_secs: int) -> Optional[str]:
        link = self.__get_link(title, artist, duration_secs)
        if not link:
            return None
        url = f"{self.__base_url}{link}"
        try:
            response = self.session.get(url=url)
            response.raise_for_status()
            parsed_html = BeautifulSoup(response.text, features="lxml")
            lyrics = parsed_html.body.find('div', attrs={'class':'lyrics_details entity_more_info'}).find('span').get_text()
            return lyrics
        except Exception:
            _LOGGER.exception(f'Could not get lyrics from link: {url}')
            return None
