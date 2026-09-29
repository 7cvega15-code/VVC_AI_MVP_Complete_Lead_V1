import json
import os
import tempfile
from pathlib import Path


def load_review_items(file_path: Path) -> list[dict]:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    if not file_path.exists():
        save_review_items(file_path, [])
        return []

    with file_path.open("r", encoding="utf-8") as review_file:
        return json.load(review_file)


def save_review_items(file_path: Path, review_items: list[dict]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            json.dump(review_items, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, file_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()