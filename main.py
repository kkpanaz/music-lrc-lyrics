from pathlib import Path
import argparse
from backends import helpers
from lyrics_getter import LyricsGetter

import logging

_LOGGER = logging.getLogger(__name__)

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Get lyrics from a range of websites and save them in LRC format.")
    parser.add_argument("-b", "--backend", help="Which website to use as a backend. Multiple can be specified. Uses all available backends by default.", action="append", default=helpers.get_all_backends())
    parser.add_argument("-i", "--input-file", help="Path of file containing songs to get lyrics for. Using sample input by default.", type=str, default="sample/input.txt")
    parser.add_argument("-s", "--input-separator", help="Separator that the input file is using. Uses `|` by default.", type=str, default="|")
    parser.add_argument("-o", "--output-folder", help="Folder where LRC lyrics should be saved. Uses sample output by default.", type=str, default="sample/output/")
    args = parser.parse_args()
    _LOGGER.info(f"Args: {args}")

    args.backends = []
    for backend_name in args.backend:
        backend_class = helpers.get_backend_class(backend_name)
        if not backend_class:
            _LOGGER.warning(f"Can't find backend {backend_name}")
        _LOGGER.info(f"Using backend: {backend_name}")
        args.backends.append(backend_class())

    args.input_path = Path(Path.cwd(), args.input_file)
    _LOGGER.info(f"Using input path: {args.input_path}")

    args.output_path = Path(Path.cwd(), args.output_folder)
    _LOGGER.info(f"Using output path: {args.output_path}")

    return args

def main() -> None:
    logging.basicConfig(level=logging.INFO)
    args = get_args()
    get_lyrics = LyricsGetter(args.backends, args.input_path, args.output_path, args.input_separator)
    get_lyrics.run()

if __name__ == "__main__":
    main()