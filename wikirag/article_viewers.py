"""Article viewer backends for LocalLLM with Wikipedia."""

from __future__ import annotations

import atexit
import subprocess
import time
import webbrowser
from abc import ABC, abstractmethod
from pathlib import Path
from urllib.parse import quote, urlparse

from .viewer_config import (
    JSONL_VIEWER_DATABASE,
    JSONL_VIEWER_DIR,
    KIWIX_EXECUTABLE,
    KIWIX_URL,
    find_kiwix_zim,
)


class _KiwixServer:
    """Small process wrapper used only by the optional Kiwix backend."""

    def __init__(self, *, executable: Path, zim_file: Path, host: str, port: int) -> None:
        self.executable = Path(executable)
        self.zim_file = Path(zim_file)
        self.host = host
        self.port = port
        self.process: subprocess.Popen | None = None

    def start(self) -> None:
        if self.process is not None and self.process.poll() is None:
            return
        self.process = subprocess.Popen(
            [
                str(self.executable),
                "--address",
                self.host,
                "--port",
                str(self.port),
                str(self.zim_file),
            ],
            cwd=str(self.executable.parent),
        )
        time.sleep(0.4)
        if self.process.poll() is not None:
            raise RuntimeError(
                f"Kiwix Server exited during startup with code {self.process.returncode}."
            )

    def stop(self) -> None:
        if self.process is None:
            return
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)
        self.process = None


class ArticleViewer(ABC):
    """Common interface for article viewer backends."""

    name: str

    @abstractmethod
    def validate(self) -> None:
        """Validate required files and settings."""

    @abstractmethod
    def open(self, title: str) -> None:
        """Open an article by title."""

    def close(self) -> None:
        """Release resources owned by the viewer."""


class JsonlArticleViewer(ArticleViewer):
    """Launch the SQLite-backed Wikipedia JSONL viewer."""

    name = "jsonl"

    def __init__(
        self,
        tool_dir: Path = JSONL_VIEWER_DIR,
        database: Path = JSONL_VIEWER_DATABASE,
    ) -> None:
        self.tool_dir = Path(tool_dir).resolve()
        self.database = Path(database).resolve()
        self.script = self.tool_dir / "wikipedia_jsonl_viewer.py"

    def validate(self) -> None:
        required = (self.script, self.database)
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            joined = "\n  - ".join(missing)
            raise FileNotFoundError(
                "Wikipedia JSONL viewer files were not found:\n"
                f"  - {joined}\n"
                f"Viewer directory: {self.tool_dir}\n"
                f"Database: {self.database}"
            )

    def open(self, title: str) -> None:
        subprocess.Popen(
            [
                "py",
                str(self.script),
                "--db",
                str(self.database),
                "--title",
                title,
            ],
            cwd=str(self.tool_dir),
            close_fds=True,
        )


class KiwixArticleViewer(ArticleViewer):
    """Optional Kiwix-backed article viewer."""

    name = "kiwix"

    def __init__(self, *, url: str, zim_name: str, executable: Path, zim_file: Path) -> None:
        self.url = url
        self.zim_name = zim_name
        self.executable = Path(executable).resolve()
        self.zim_file = Path(zim_file).resolve()
        self._server: _KiwixServer | None = None

    def validate(self) -> None:
        if not self.executable.is_file():
            raise FileNotFoundError(f"Kiwix executable not found: {self.executable}")
        if not self.zim_file.is_file():
            raise FileNotFoundError(f"Kiwix ZIM file not found: {self.zim_file}")

    def start(self) -> None:
        self.validate()
        self._server = _KiwixServer(
            executable=self.executable,
            zim_file=self.zim_file,
            host="127.0.0.1",
            port=urlparse(self.url).port or 8080,
        )
        self._server.start()
        atexit.register(self.close)

    def open(self, title: str) -> None:
        if self._server is None:
            raise RuntimeError("Kiwix Server is not running.")
        normalized_title = title.strip().replace(" ", "_")
        encoded_title = quote(normalized_title, safe="")
        article_url = (
            f"{self.url.rstrip('/')}/viewer#"
            f"{self.zim_name}/{encoded_title}"
        )
        webbrowser.open(article_url, new=2)

    def close(self) -> None:
        if self._server is not None:
            self._server.stop()
            self._server = None


def create_article_viewer(*, viewer_name: str) -> ArticleViewer:
    """Create and validate the selected viewer backend."""

    if viewer_name == "jsonl":
        viewer = JsonlArticleViewer()
        viewer.validate()
        return viewer

    if viewer_name == "kiwix":
        zim_file = find_kiwix_zim()
        if zim_file is None:
            raise FileNotFoundError("Kiwix ZIM file not found.")

        viewer = KiwixArticleViewer(
            url=KIWIX_URL,
            zim_name=zim_file.stem,
            executable=KIWIX_EXECUTABLE,
            zim_file=zim_file,
        )
        viewer.start()
        return viewer

    raise ValueError(f"Unsupported viewer: {viewer_name}")
