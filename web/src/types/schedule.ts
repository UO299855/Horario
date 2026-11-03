import type { ScheduleSourceId } from "../config";

// One row of a schedule CSV, keyed by the trimmed header names
export type CsvRow = Record<string, string | undefined>;

// A parsed class session
export interface ScheduleSession {
  id: number;
  subject: string;
  date: Date;
  startTime: string;
  endTime: string;
  description: string;
  location: string;
}

// A session tagged with the timetable it comes from, ready for the calendar
export interface CalendarEvent extends ScheduleSession {
  sourceId: ScheduleSourceId;
}