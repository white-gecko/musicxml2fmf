# MusicXML to Flipper Music Format

This script reads a (not compressed) [MusicXML](https://www.w3.org/2021/06/musicxml40/) ([Wikipedia](https://en.wikipedia.org/wiki/MusicXML)) file and transforms it to the [Flipper Music Format](https://github.com/Tonsil/flipper-music-files) which can be executed on the [Flipper Zero](https://flipperzero.one/).

This allows to compose your music with graphical tools like [MuseScore](https://en.wikipedia.org/wiki/MuseScore) and play the music on the Flipper.

## Installation

To install the script you need [poetry](https://python-poetry.org/).

Run:

```
$ poetry install
…
$ poetry run musicxml2fmf --help
```

## TODO
- Tests
- Changelog
- Support for multiple parts: selection of a part to convert
- get bpm based on the tempo given in musicxml
- Don't write out the octave and duration if it is the same as the default
