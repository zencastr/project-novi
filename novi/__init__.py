from pathlib import Path


def read_sample_file(urlfile: Path) -> list[str]:
    return [u for u in urlfile.read_text().split("\n") if u and not u.startswith("#")]