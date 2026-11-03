# software_schedule_downloader.py
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "keys.env"


class SoftwareScheduleDownloader:
    def __init__(self, env_file: Path = ENV_FILE):
        load_dotenv(env_file)
        self.file_url = os.getenv("SOFTWARE_FILE_URL")
        if not self.file_url:
            raise ValueError(f"Missing FILE_URL in {env_file}")

    def _direct_download_url(self) -> str:
        # Asks SharePoint to send the file instead of opening the viewer
        separator = "&" if "?" in (self.file_url or "") else "?"
        return f"{self.file_url}{separator}download=1"

    def download(self, destination: str | Path) -> Path:
        """Downloads the file and saves it to `destination`."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)

        response = requests.get(self._direct_download_url(), timeout=60, allow_redirects=True)
        response.raise_for_status()

        
        destination.write_bytes(response.content)
        return destination


if __name__ == "__main__":
    downloader = SoftwareScheduleDownloader()
    path = downloader.download(BASE_DIR / "downloads" / "new_software_schedule.csv")
    print(f"Download completed: {path}")