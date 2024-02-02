"""
vtt utilities
"""

from pathlib import Path

import webvtt


def vtt_to_utterances(vtt_path: Path) -> list[str]:
    """
    reads vtt file and spits out utterances formatted like:
    START\tEND\tTEXT
    """
    s = webvtt.read(vtt_path)
    return [f"{c.start}\t{c.end}\t{c.text}" for c in s.captions]
