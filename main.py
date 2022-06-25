from distutils.debug import DEBUG
from pathlib import Path
import argparse
from backends import helpers
from lyrics_getter import LyricsGetter

import logging

_LOGGER = logging.getLogger(__name__)

def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser("Get lyrics from a range of websites and save them in LRC format.")
    parser.add_argument("-b", "--backend", help="Which website to use as a backend. Multiple can be specified. Uses all available backends by default.", action="append", default=[])
    parser.add_argument("-i", "--input-file", help="Path of file containing songs to get lyrics for. Using sample input by default.", type=str, default="sample/input.txt")
    parser.add_argument("-s", "--input-separator", help="Separator that the input file is using. Uses `|` by default.", type=str, default="|")
    parser.add_argument("-o", "--output-folder", help="Folder where LRC lyrics should be saved. Uses sample output by default.", type=str, default="sample/output/")
    parser.add_argument("--no-timestamp-fallback", help="Store lyrics without timestamps (in txt file) if no timed lyrics found. Will append all non-timestamp backends onto existing list. Default false.", action="store_true")
    parser.add_argument("--genius-access-token", help="An access token provided from your free Genius account.", type=str, default=None)
    parser.add_argument("-v", "--verbose", help="Set logging level to verbose/debug.", action="store_true")
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level)

    args.input_path = Path(Path.cwd(), args.input_file)
    args.output_path = Path(Path.cwd(), args.output_folder)

    if not args.backend:
        args.backend = helpers.get_all_backends()
    if args.no_timestamp_fallback:
        args.backend.extend(helpers.get_all_no_timestamp_backends())

    dont_print_args = ["genius-access-token"]
    _LOGGER.debug(f"Args:")
    for key, value in vars(args).items():
        if key not in dont_print_args:
            _LOGGER.debug(f"    {key}: {value}")

    timestamp_backends = []
    non_timestamp_backends = []
    existing_backends = []
    for backend_name in args.backend:
        # Don't allow duplicate backends
        if backend_name in existing_backends:
            continue

        backend_class = helpers.get_backend_class(backend_name)
        if not backend_class:
            _LOGGER.warning(f"Can't find backend {backend_name}")
        _LOGGER.debug(f"Using backend: {backend_name}")
        if helpers.has_timestamps(backend_name):
            timestamp_backends.append(backend_class(args))
        else:
            non_timestamp_backends.append((backend_class(args)))
        existing_backends.append(backend_name)

    # Enfore that we use timestamp backends first
    args.backends = timestamp_backends + non_timestamp_backends

    if not args.backends:
        raise ValueError("No valid backends provided")

    return args

def main() -> None:
    args = get_args()
    get_lyrics = LyricsGetter(args.backends, args.input_path, args.output_path, args.input_separator)
    get_lyrics.run()

if __name__ == "__main__":
    main()