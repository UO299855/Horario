#!/usr/bin/env python3
"""
Converts the university timetable (Excel weekly grid) into a CSV with the
same format as the software timetable.

Input:
    math_schedule.xlsx   Weekly grid downloaded from the university.

Output:
    A CSV with the columns:
    Subject, Start Date, Start Time, End Date, End Time, Description, Location

Usage:
    from math_schedule_converter import MathScheduleConverter

    MathScheduleConverter(r"D:\\UNIOVI\\Horario\\math_schedule.xlsx").convert(
        r"D:\\UNIOVI\\Horario\\math_schedule.csv"
    )
"""
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import openpyxl

CS_LOCATION = "Escuela Ing. Inf."  # classes at this location are computer science
HEADER = "Subject, Start Date, Start Time, End Date, End Time,  Description, Location"
TIME_RE = re.compile(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$")
DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
SEMESTER_RE = re.compile(r"^(1er|2º) Semestre")


@dataclass
class Session:
    day: date
    start: str  # "HH:MM"
    end: str    # "HH:MM"
    subject: str
    location: str
    semester: str = ""

    @property
    def hours(self) -> int:
        h1, m1 = map(int, self.start.split(":"))
        h2, m2 = map(int, self.end.split(":"))
        return round(((h2 * 60 + m2) - (h1 * 60 + m1)) / 60)


class MathScheduleConverter:
    def __init__(self, excel_path):
        self.excel_path = Path(excel_path)

    def convert(self, output_path, exclude_cs: bool = False) -> Path:
        """
        Writes the timetable as a software-format CSV.

        exclude_cs=False (default): every class in the grid is exported.
        exclude_cs=True: classes at CS_LOCATION are skipped.
        """
        sessions = self._join_consecutive(self._parse_grid())
        if exclude_cs:
            sessions = [s for s in sessions if s.location != CS_LOCATION]

        rows = self._to_rows(sessions)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self._render(rows), encoding="utf-8")
        print(f"CSV generado: {output_path} ({len(rows)} sesiones)")
        return output_path

    # ---------- Reading the Excel grid ----------

    def _parse_grid(self) -> list[Session]:
        """Reads every 'time | subject | location' block of the weekly grid."""
        ws = openpyxl.load_workbook(self.excel_path, data_only=True).active
        if ws is None:
            raise ValueError(f"{self.excel_path} has no active sheet.")

        week_rows = [c.row for c in ws["A"] if isinstance(c.value, str) and "Semana" in c.value]
        week_rows.append(ws.max_row + 1)

        sessions = []
        for top, bottom in zip(week_rows, week_rows[1:]):
            semester_match = SEMESTER_RE.match(str(ws.cell(row=top, column=1).value or ""))
            semester = semester_match.group(1) if semester_match else ""

            # Day headers ("Lunes, 07/09/2026") sit on the week row; each day spans 3 columns
            day_columns = {}
            for col in range(2, ws.max_column + 1):
                value = ws.cell(row=top, column=col).value
                if isinstance(value, str) and (m := DATE_RE.search(value)):
                    day_columns[col] = date(int(m[3]), int(m[2]), int(m[1]))

            for col, day in day_columns.items():
                for row in range(top + 1, bottom):
                    time_value = ws.cell(row=row, column=col).value
                    if not (isinstance(time_value, str) and (m := TIME_RE.match(time_value))):
                        continue
                    subject = ws.cell(row=row, column=col + 1).value
                    location = ws.cell(row=row, column=col + 2).value
                    if not subject:
                        continue
                    sessions.append(Session(
                        day=day,
                        start=f"{m[1]}:{m[2]}",
                        end=f"{m[3]}:{m[4]}",
                        subject=str(subject).strip(),
                        location=str(location or "").strip(),
                        semester=semester,
                    ))
        return sessions

    @staticmethod
    def _join_consecutive(sessions: list[Session]) -> list[Session]:
        """Joins one-hour grid cells with the same subject and location into one session."""
        sessions = sorted(sessions, key=lambda s: (s.day, s.start))
        merged: list[Session] = []
        for s in sessions:
            if merged:
                last = merged[-1]
                if (last.day, last.subject, last.location, last.end) == (s.day, s.subject, s.location, s.start):
                    last.end = s.end
                    continue
            merged.append(Session(**vars(s)))
        return merged

    # ---------- Building the software-format rows ----------

    @staticmethod
    def _to_rows(sessions: list[Session]) -> list[dict]:
        """Adds 'Hora de clase número N' descriptions, with N = cumulative hours per subject and semester."""
        totals: dict[tuple, int] = {}
        rows = []
        for s in sorted(sessions, key=lambda s: (s.day, s.start)):
            key = (s.subject, s.semester)
            totals[key] = totals.get(key, 0) + s.hours
            rows.append({
                "subject": s.subject,
                "start_date": s.day,
                "start": s.start,
                "end_date": s.day,
                "end": s.end,
                "description": f"Hora de clase número {totals[key]} de {s.subject}",
                "location": s.location,
            })
        return rows

    @staticmethod
    def _render(rows: list[dict]) -> str:
        lines = [HEADER, ""]
        for r in rows:
            sd = r["start_date"].strftime("%d/%m/%Y")
            ed = r["end_date"].strftime("%d/%m/%Y")
            st = r["start"].replace(":", ".")
            et = r["end"].replace(":", ".")
            lines.append(f"{r['subject']}, {sd}, {st:>6},{ed}, {et},{r['description']}, {r['location']}")
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    BASE = Path(__file__).resolve().parent
    MathScheduleConverter(BASE / "downloads" / "math_schedule.xlsx").convert(
        BASE / "downloads" / "math_schedule.csv"
    )