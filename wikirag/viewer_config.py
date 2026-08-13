from pathlib import Path

RAG_ROOT = Path(__file__).resolve().parents[2]

TOOLS_DIR = RAG_ROOT / "tools"
DATA_DIR = RAG_ROOT / "data"

JSONL_VIEWER_DIR = TOOLS_DIR / "wikipedia_viewer"
JSONL_VIEWER_DATABASE = DATA_DIR / "wikipedia_viewer" / "wikipedia_articles.sqlite3"

KIWIX_DIR = TOOLS_DIR / "kiwix"
KIWIX_DATA_DIR = DATA_DIR / "kiwix"

KIWIX_EXECUTABLE = KIWIX_DIR / "kiwix-serve.exe"
KIWIX_URL = "http://127.0.0.1:8080"


def find_kiwix_zim() -> Path | None:
    zim_files = sorted(KIWIX_DATA_DIR.glob("*.zim"))
    return zim_files[0] if zim_files else None
