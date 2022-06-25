import logging
import re
from backends.base import GetLyricsBase

_LOGGER = logging.getLogger(__name__)


class GetLyricsRCLyricsBand(GetLyricsBase):
    def __init__(self, args):
        super().__init__(args)
        self.name = "rclyricsband"
        self.has_timestamps = True
        self.base_url = "https://rclyricsband.com"
        self.search_url = self.base_url
        self.query_key = "s"
        self.link_includes_base = True
        self.link_strainer_args = {"name": "div", "attrs": {"id": "content"}}
        self.link_result_args = {"name": "a"}
        self.lyrics_strainer_args = {
            "name": "div",
            "attrs": {"class": "su-box-content su-u-clearfix su-u-trim"},
        }

    def scrub_lyrics(self, lyrics: str) -> str:
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
