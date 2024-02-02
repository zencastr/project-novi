"""
download audio from youtube videos, along with their chapters and metadata
"""

import json
from pathlib import Path
import tempfile

from yt_dlp import YoutubeDL

from novi import read_sample_file


option_defaults = {
    'extract_flat': 'discard_in_playlist',
    'fragment_retries': 10,
    'ignoreerrors': 'only_download',
    'postprocessors': [{'key': 'FFmpegConcat',
                        'only_multi_video': True,
                        'when': 'playlist'}],
    'retries': 10,
}


def good_ids_from_infojsons(output_path: Path) -> set[str]:
    """
    return the set of ids that have chapters and are longer than 10m given a download dir
    filenames MUST be in format %(id)s.info.json
    """
    good_ids = set()
    for path in output_path.iterdir():
        if str(path).endswith('.info.json'):
            id_data = json.loads(path.read_text())
            duration = id_data.get('duration')
            chs = id_data.get('chapters')
            if chs is not None:
                if isinstance(chs, list) and len(chs) > 1:
                    if duration > 600:  # 10m
                        good_ids.add(path.stem.split('.')[0])
    return good_ids


def ensure_chapters(urls: list[str]) -> list[str]:
    """
    Given a list of urls (videos, channels, playlist, whatever), return a list of ids that have chapters
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir)
        options = {
            **option_defaults,
            'outtmpl': {'default': f'{output_path}/%(id)s.%(ext)s'},
            'skip_download': True,
            'writeinfojson': True,
        }
        with YoutubeDL(options) as ydl:
            ydl.download(urls)
        good_ids = good_ids_from_infojsons(output_path)
    return list(good_ids)


def download_audio_and_subs_from_urls(urls: list[str], output_dir: Path):
    """
    yt-dlp --embed-chapters --extract-audio -o $outputdir/%(id)s.%(ext)s $url
    options generated with https://github.com/yt-dlp/yt-dlp/blob/5f25f348f9eb5db842b1ec6799f95bebb7ba35a7/devscripts/cli_to_api.py
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    options = {
        **option_defaults,
        'format': 'bestaudio/best',
        'outtmpl': {'default': f'{output_dir}/%(id)s.%(ext)s'},
        'writeautomaticsub': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio',
                            'nopostoverwrites': False,
                            'preferredcodec': 'best',
                            'preferredquality': '5'},
                            {'add_chapters': True,
                            'add_infojson': None,
                            'add_metadata': True,
                            'key': 'FFmpegMetadata'}],
    }
    with YoutubeDL(options) as ydl:
        ydl.download(urls)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("urlfile", type=Path, help="path to newline-separted file of urls")
    parser.add_argument("--output-dir", type=Path, default=Path.cwd() / "downloads")
    args = parser.parse_args()
    urls = read_sample_file(args.urlfile)
    urls = ensure_chapters(urls)
    download_audio_and_subs_from_urls(urls, args.output_dir)