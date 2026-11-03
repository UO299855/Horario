#!/usr/bin/env python3
"""
Merges the university timetable (Excel grid) with the computer science timetable
(software CSV) into one CSV in the software format, and exports the Excel grid
to the same CSV format.

Sources:
    math_schedule.xlsx   Weekly grid from the university (Excel Online download).
                         Classes located at "Escuela Ing. Inf." are computer science
                         classes; the merger ignores them because they come from the software CSV.
    software_base.csv    Computer science timetable in software format (maintained by you).

Outputs:
    software_schedule.csv  software_base.csv + the non-CS sessions from the Excel grid.
                           Overwritten only when the merged result actually changes.
    Via export_math_schedule(): a CSV with the sessions of the Excel grid in software format.
"""
import csv
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import openpyxl

CS_LOCATION = "Escuela Ing. Inf."
HEADER = "Subject, Start Date, Start Time, End Date, End Time,  Description, Location"
TIME_RE = re.compile(r"^(\d{2}):(\d{2})-(\d{2}):(\d{2})$")
DATE_RE = re.compile(r"(\d{2})/(\d{2})/(\d{4})")
SEMESTER_RE = re.compile(r"^(1er|2º) Semestre")


@dataclass
class Session:
    day: date
    start: str        # "HH:MM"
    end: str          # "HH:MM"
    subject: str
    location: str
    semester: str = ""

    @property
    def hours(self) -> int:
        h1, m1 = map(int, self.start.split(":"))
        h2, m2 = map(int, self.end.split(":"))
        return round(((h2 * 60 + m2) - (h1 * 60 + m1)) / 60)


class ScheduleMerger:
    def __init__(self, excel_path, software_base_path, output_path):
        self.excel_path = Path(excel_path)
        self.software_base_path = Path(software_base_path) if software_base_path else None
        self.output_path = Path(output_path)

    # ---------- Excel grid -> sessions ----------

    def _parse_grid(self) -> list[Session]:
        """Reads every 'time | subject | location' block in the weekly grid."""
        ws = openpyxl.load_workbook(self.excel_path, data_only=True).active
        if ws is None:
            raise ValueError(f"Excel file {self.excel_path} has no active sheet.")
        week_rows = [c.row for c in ws["A"] if isinstance(c.value, str) and "Semana" in c.value]
        week_rows.append(ws.max_row + 1)

        sessions = []
        for top, bottom in zip(week_rows, week_rows[1:]):
            semester_match = SEMESTER_RE.match(str(ws.cell(row=top, column=1).value or ""))
            semester = semester_match.group(1) if semester_match else ""

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
        """Merges one-hour grid cells with the same subject and location into one session."""
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

    def _non_cs_sessions(self) -> list[Session]:
        grid = self._parse_grid()
        non_cs = [s for s in grid if s.location != CS_LOCATION]
        return self._join_consecutive(non_cs)

    # ---------- Software CSV ----------

    def _read_software_base(self) -> list[dict]:
        if not self.software_base_path or not self.software_base_path.exists():
            return []
        return self._read_software_csv(self.software_base_path)

    @staticmethod
    def _read_software_csv(path: Path) -> list[dict]:
        rows = []
        with path.open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            next(reader, None)  # header
            for raw in reader:
                fields = [c.strip() for c in raw]
                if len(fields) < 7 or not fields[0]:
                    continue
                rows.append({
                    "subject": fields[0],
                    "start_date": datetime.strptime(fields[1], "%d/%m/%Y").date(),
                    "start": fields[2].replace(".", ":").zfill(5),
                    "end_date": datetime.strptime(fields[3], "%d/%m/%Y").date(),
                    "end": fields[4].replace(".", ":").zfill(5),
                    "description": fields[5],
                    "location": fields[6],
                })
        return rows

    def _read_output_rows(self) -> list[dict]:
        return self._read_software_csv(self.output_path)

    # ---------- Building the rows ----------

    @staticmethod
    def _numbered_descriptions(sessions: list[Session]) -> list[tuple[Session, str]]:
        """'Hora de clase número N de SUBJ', with N = cumulative hours per subject and semester."""
        totals: dict[tuple, int] = {}
        descriptions = []
        for s in sorted(sessions, key=lambda s: (s.day, s.start)):
            key = (s.subject, s.semester)
            totals[key] = totals.get(key, 0) + s.hours
            descriptions.append((s, f"Hora de clase número {totals[key]} de {s.subject}"))
        return descriptions

    @classmethod
    def _sessions_to_rows(cls, sessions: list[Session]) -> list[dict]:
        rows = []
        for session, description in cls._numbered_descriptions(sessions):
            rows.append({
                "subject": session.subject,
                "start_date": session.day,
                "start": session.start,
                "end_date": session.day,
                "end": session.end,
                "description": description,
                "location": session.location,
            })
        rows.sort(key=lambda r: (r["start_date"], r["start"], r["subject"]))
        return rows

    def _build_rows(self) -> list[dict]:
        software = self._read_software_base()
        mates = self._sessions_to_rows(self._non_cs_sessions())
        rows = software + mates
        rows.sort(key=lambda r: (r["start_date"], r["start"], r["subject"]))
        return rows

    # ---------- Rendering and comparison ----------

    @staticmethod
    def _format_row(r: dict) -> str:
        sd = r["start_date"].strftime("%d/%m/%Y")
        ed = r["end_date"].strftime("%d/%m/%Y")
        st = r["start"].replace(":", ".")
        et = r["end"].replace(":", ".")
        return f"{r['subject']}, {sd}, {st:>6},{ed}, {et},{r['description']}, {r['location']}"

    def _render(self, rows: list[dict]) -> str:
        lines = [HEADER, ""] + [self._format_row(r) for r in rows]
        return "\n".join(lines) + "\n"

    @staticmethod
    def _key(rows: list[dict]) -> list[tuple]:
        return [tuple(sorted(r.items(), key=lambda kv: kv[0])) for r in rows]

    def _warn_conflicts(self, rows: list[dict]) -> None:
        """Reports sessions that overlap in time (same day and intersecting hours)."""
        for i, a in enumerate(rows):
            for b in rows[i + 1:]:
                if a["start_date"] == b["start_date"] and a["start"] < b["end"] and b["start"] < a["end"]:
                    print(f"  AVISO solape: {a['subject']} {a['start']}-{a['end']} "
                          f"y {b['subject']} {b['start']}-{b['end']} el {a['start_date']:%d/%m/%Y}")

    # ---------- Public entry point ----------

    def run(self) -> bool:
        """Returns True if the output file was written (the merged result changed)."""
        rows = self._build_rows()

        if self.output_path.exists():
            if self._key(self._read_output_rows()) == self._key(rows):
                print("Sin cambios: el horario de software ya está actualizado.")
                return False

        self._warn_conflicts(rows)
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        self.output_path.write_text(self._render(rows), encoding="utf-8")
        print(f"Horario actualizado: {self.output_path} ({len(rows)} filas)")
        return True


def export_math_schedule(excel_path, output_path, exclude_cs: bool = False) -> Path:
    """
    Converts the university Excel grid into a CSV with the software format.

    exclude_cs=False (default): every class in the grid is exported.
    exclude_cs=True: classes at CS_LOCATION are skipped.
    """
    output_path = Path(output_path)
    merger = ScheduleMerger(excel_path, software_base_path=None, output_path=output_path)

    sessions = merger._join_consecutive(merger._parse_grid())
    if exclude_cs:
        sessions = [s for s in sessions if s.location != CS_LOCATION]

    rows = ScheduleMerger._sessions_to_rows(sessions)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(merger._render(rows), encoding="utf-8")
    print(f"CSV generado: {output_path} ({len(rows)} sesiones)")
    return output_path


if __name__ == "__main__":
    BASE = Path(__file__).resolve().parent

    # 1) Merge: software CSV + non-CS classes from the Excel grid
    ScheduleMerger(
        excel_path=BASE / "downloads" / "math_schedule.xlsx",
        software_base_path=BASE / "downloads" / "software_base.csv",
        output_path=BASE / "downloads" / "math_schedule.csv",
    ).run()

    # 2) Export only the Excel grid to software format (optional)
    # export_math_schedule(BASE / "math_schedule.xlsx", BASE / "math_schedule.csv")