from math_downloader import MathDownloader
from software_downloader import SoftwareScheduleDownloader
from schedule_converter import MathScheduleConverter

from dotenv import load_dotenv
from pathlib import Path
import os
import openpyxl

class Dispatcher:
    def __init__(self):
        self.base_dir = Path(__file__).resolve().parent
        env_file = self.base_dir / "keys.env"
        load_dotenv(env_file)
        software_file_url = os.getenv("SOFTWARE_FILE_URL")
        if not software_file_url:
            raise ValueError(f"Missing SOFTWARE_FILE_URL in {env_file}")
        self.software_downloader = SoftwareScheduleDownloader(env_file=env_file)
        math_file_url = os.getenv("MATH_FILE_URL")
        if not math_file_url:
            raise ValueError(f"Missing MATH_FILE_URL in {env_file}")
        self.math_downloader = MathDownloader(math_file_url)

    def run(self):
        base_destination = self.base_dir.parent / "web" / "public"
        math_destination = self.base_dir / "downloads" / "new_math_schedule.xlsx"
        software_destination = base_destination / "new_software_schedule.csv"

        self.math_downloader.download(math_destination)
        self.software_downloader.download(software_destination)

        existing_math_schedule = self.base_dir / "downloads" / "math_schedule.xlsx"
        existing_software_schedule = base_destination / "software_schedule.csv"
        final_math_schedule = base_destination / "math_schedule.csv"

        math_changes_detected = self._xlsx_changes_made(existing_math_schedule, math_destination)
        if math_changes_detected:
            print("Math schedule has changed. Updating the existing file.")
            math_destination.replace(existing_math_schedule)
            MathScheduleConverter(
                excel_path=existing_math_schedule,
            ).convert(
                output_path= final_math_schedule,
                exclude_cs=True
            )

        software_changes_detected = self._lines_changes_made(existing_software_schedule, software_destination)
        if software_changes_detected:
            print("Software schedule has changed. Updating the existing file.")
            software_destination.replace(existing_software_schedule)


    def _lines_changes_made(self, existing: Path, new: Path) -> bool:
        """True if both files have the same normalized text lines."""
        if not existing.exists():
            return True
        return self._text_lines(existing) == self._text_lines(new)

    def _xlsx_changes_made(self, existing: Path, new: Path) -> bool:
        """True if both Excel files have the same cell values in every sheet."""
        if not existing.exists():
            return True
        return self._xlsx_cells(existing) == self._xlsx_cells(new)

    def _text_lines(self, path: Path) -> list[str]:
        """Normalized text lines: ignores line endings, BOM and trailing whitespace."""
        text = path.read_text(encoding="utf-8-sig")
        return [line.rstrip() for line in text.splitlines()]

    def _xlsx_cells(self,path: Path) -> dict:
        """Cell values of every sheet, ignoring styles and document metadata."""
        wb = openpyxl.load_workbook(path, data_only=True)
        content = {}
        for ws in wb.worksheets:
            content[ws.title] = [
                [cell.value for cell in row]
                for row in ws.iter_rows()
            ]
        return content


def main():
    Dispatcher().run()

if __name__ == "__main__":
    main()