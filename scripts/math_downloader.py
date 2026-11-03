#!/usr/bin/env python3
"""
Downloads a file from Excel Online by reusing a session that you start manually
(with MFA). Your password is never stored.

Setup:
    pip install playwright
    python -m playwright install chromium

Files next to this script:
    keys.env      -> FILE_URL (and optionally LOGIN_URL)
    session.json  -> session cookies (sensitive, do not commit to Git)

Usage:
    downloader = ExcelOnlineDownloader(file_url=url)
    downloader.download("any/folder/any_name.xlsx")
"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / "keys.env"
DEFAULT_SESSION_FILE = BASE_DIR / "session.json"
DEFAULT_LOGIN_URL = "https://www.office.com/"
EXCEL_FRAME_SELECTOR = 'iframe[name="WacFrame_Excel_0"]'
TIMEOUT_LOAD_MS = 60_000
TIMEOUT_DOWNLOAD_MS = 60_000


def load_env(path: Path) -> dict:
    if not path.exists():
        sys.exit(f"No existe {path}. Crea el archivo con al menos FILE_URL=...")
    values = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


class MathDownloader:
    def __init__(
        self,
        file_url: str,
        session_file: Path = DEFAULT_SESSION_FILE,
        login_url: str = DEFAULT_LOGIN_URL,
        headless: bool = True,
    ):
        self.file_url = file_url
        self.session_file = Path(session_file)
        self.login_url = login_url
        self.headless = headless

    def download(self, destination: str | Path) -> Path:
        """Downloads a copy of the file and saves it to `destination`."""
        destination = Path(destination)
        destination.parent.mkdir(parents=True, exist_ok=True)

        with sync_playwright() as playwright:
            if not self.session_file.exists():
                self._login_manually(playwright)
            return self._download_copy(playwright, destination)

    def _login_manually(self, playwright) -> None:
        print("Se abrirá un navegador. Inicia sesión con tu cuenta de la universidad y completa el MFA.")
        browser = playwright.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context()
        page = context.new_page()
        page.goto(self.login_url)
        input("Cuando veas tu sesión iniciada en Office, pulsa Enter aquí... ")
        context.storage_state(path=str(self.session_file))
        browser.close()
        print(f"Sesión guardada en {self.session_file}")

    def _download_copy(self, playwright, destination: Path) -> Path:
        browser = playwright.chromium.launch(headless=self.headless)
        context = browser.new_context(
            storage_state=str(self.session_file),
            accept_downloads=True,
        )
        page = context.new_page()

        try:
            page.goto(self.file_url, wait_until="domcontentloaded")

            if "login.microsoftonline.com" in page.url or "login.live.com" in page.url:
                raise RuntimeError(
                    f"La sesión ha caducado. Borra {self.session_file} y vuelve a ejecutar el script."
                )

            excel = page.frame_locator(EXCEL_FRAME_SELECTOR)

            # File > Make a copy > Download a copy (in Spanish: Archivo > Crear una copia > Descargar una copia)
            excel.get_by_role("button", name="Archivo").click(timeout=TIMEOUT_LOAD_MS)
            excel.get_by_text("Crear una copia", exact=True).click()

            download_option = excel.get_by_text("Descargar una copia", exact=True)
            try:
                download_option.wait_for(state="visible", timeout=3_000)
            except PlaywrightTimeout:
                # If the submenu does not open on click, open it with the keyboard
                excel.get_by_role("menuitem", name="Crear una copia").press("ArrowRight")
                download_option.wait_for(state="visible", timeout=5_000)

            with page.expect_download(timeout=TIMEOUT_DOWNLOAD_MS) as download_info:
                download_option.click()

            download_info.value.save_as(str(destination))
            return destination
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    env = load_env(ENV_FILE)
    downloader = MathDownloader(
        file_url=env["MATH_FILE_URL"],
        login_url=env.get("LOGIN_URL", DEFAULT_LOGIN_URL),
        headless=True,  # set to True once it works reliably for you
    )
    saved_path = downloader.download(BASE_DIR / "downloads" / "new_math_schedule.xlsx")
    print(f"Descarga completada: {saved_path}")