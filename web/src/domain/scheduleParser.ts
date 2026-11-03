import Papa from "papaparse";
import type { CsvRow, ScheduleSession } from "../types/schedule";

// Column names as they appear in the CSV header, after trimming whitespace
const COLUMN = {
  subject: "Subject",
  startDate: "Start Date",
  startTime: "Start Time",
  endTime: "End Time",
  description: "Description",
  location: "Location",
} as const;

const DATE_PATTERN = /^(\d{2})\/(\d{2})\/(\d{4})$/;
const TIME_PATTERN = /^(\d{1,2})[.:](\d{2})$/;

// "15/09/2026" -> Date, or null if the text is not a valid date
function parseDate(text: string | undefined): Date | null {
  const match = DATE_PATTERN.exec(text ?? "");
  if (!match) return null;

  const [, day, month, year] = match;
  return new Date(Number(year), Number(month) - 1, Number(day));
}

// "11.00" or "11:00" -> "11:00", or null if the text is not a valid time
function parseTime(text: string | undefined): string | null {
  const match = TIME_PATTERN.exec(text ?? "");
  if (!match) return null;

  const [, hours, minutes] = match;
  return `${hours.padStart(2, "0")}:${minutes}`;
}

// Converts one CSV row into a session, or returns null if required fields are missing
function toSession(row: CsvRow, index: number): ScheduleSession | null {
  const subject = row[COLUMN.subject];
  const date = parseDate(row[COLUMN.startDate]);
  const startTime = parseTime(row[COLUMN.startTime]);
  const endTime = parseTime(row[COLUMN.endTime]);

  if (!subject || !date || !startTime || !endTime) return null;

  return {
    id: index,
    subject,
    date,
    startTime,
    endTime,
    description: row[COLUMN.description] ?? "",
    location: row[COLUMN.location] ?? "",
  };
}

// Parses the CSV text into sessions sorted by date and start time
export function parseScheduleCsv(csvText: string): ScheduleSession[] {
  const { data } = Papa.parse<CsvRow>(csvText, {
    header: true,
    skipEmptyLines: true,
    transformHeader: (header) => header.trim(),
    transform: (value) => value.trim(),
  });

  return data
    .map(toSession)
    .filter((session): session is ScheduleSession => session !== null)
    .sort((a, b) => a.date.getTime() - b.date.getTime() || a.startTime.localeCompare(b.startTime));
}