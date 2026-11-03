export type ScheduleSourceId = "math" | "software";

export interface ScheduleSource {
  id: ScheduleSourceId;
  label: string;
  fileName: string;
}

// Both timetables are always shown together. Files are served from web/public/
export const SCHEDULE_SOURCES: readonly ScheduleSource[] = [
  { id: "math", label: "Matemáticas", fileName: "math_schedule.csv" },
  { id: "software", label: "Informática", fileName: "software_schedule.csv" },
];

// Calendar grid settings. The visible hours expand if an event falls outside this range.
export const HOUR_HEIGHT_PX = 64;
export const DEFAULT_START_HOUR = 9;
export const DEFAULT_END_HOUR = 22;