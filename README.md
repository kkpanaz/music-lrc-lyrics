# Music LRC Lyrics
Get lyrics for all your faviourite songs in LRC format using a range of backends (A.K.A. websites).

Also includes fallback integrations to get lyrics without timestamps (if lyrics with timestamps can't be found). These will be stored in TXT format (not LRC).

## Backends Supported
- [Megalobiz](https://www.megalobiz.com/)
- [RCLyricsBand](https://rclyricsband.com/)

## Fallback Backends (no timestamps)
- [Genius](https://genius.com/)

## How To Use
1. Create an input file containing one line per song in the format `<artist>|<title>|<duration>` where:
    - `|` can be replaced by input separator argument
    - `duration` should be in the format `<hours>:<minutes>:<seconds>` where each is a 2 digit integer
    - I suggest using a tool like [Spotlistr](https://www.spotlistr.com/export/spotify-playlist)
2. Pip install requirements.txt
3. Run `main.py` specifying input and output (uses sample by default)
    ```
    λ py main.py -h
    usage: Get lyrics from a range of websites and save them in LRC format. [-h] [-b BACKEND] [-i INPUT_FILE] [-s INPUT_SEPARATOR] [-o OUTPUT_FOLDER] [--no-timestamp-fallback]
                                                                            [--genius-access-token GENIUS_ACCESS_TOKEN] [-v]

    optional arguments:
    -h, --help            show this help message and exit
    -b BACKEND, --backend BACKEND
                            Which website to use as a backend. Multiple can be specified. Uses all available backends by default.
    -i INPUT_FILE, --input-file INPUT_FILE
                            Path of file containing songs to get lyrics for. Using sample input by default.
    -s INPUT_SEPARATOR, --input-separator INPUT_SEPARATOR
                            Separator that the input file is using. Uses `|` by default.
    -o OUTPUT_FOLDER, --output-folder OUTPUT_FOLDER
                            Folder where LRC lyrics should be saved. Uses sample output by default.
    --no-timestamp-fallback
                            Store lyrics without timestamps (in txt file) if no timed lyrics found. Will append all non-timestamp backends onto existing list. Default false.
    --genius-access-token GENIUS_ACCESS_TOKEN
                            An access token provided from your free Genius account.
    -v, --verbose         Set logging level to verbose/debug.
    ```
See `sample/` for example input and output.
