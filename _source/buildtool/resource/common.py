from pathlib import Path


def get_resources_path(data_path: Path) -> Path:
    return data_path / 'resource'
