from typing import Sequence

from .rag import ingest_paths as _ingest_paths


def ingest(paths: Sequence[str]) -> int:
    """Wrapper for CLI or scripting usage."""
    return _ingest_paths(paths)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Ingest files into the vector store")
    parser.add_argument("paths", nargs="+", help="Paths to files or directories")
    args = parser.parse_args()
    count = ingest(args.paths)
    print(f"Indexed {count} chunks")
