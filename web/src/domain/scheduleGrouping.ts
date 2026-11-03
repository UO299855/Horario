import type { DayGroup, ScheduleSession } from "../types/schedule";
import { toDayKey } from "../utils/dateFormat";

// Keeps the sessions whose subject, location or description contain the query
export function filterSessions(sessions: ScheduleSession[], query: string): ScheduleSession[] {
  const normalizedQuery = query.trim().toLowerCase();
  if (!normalizedQuery) return sessions;

  return sessions.filter((session) =>
    [session.subject, session.location, session.description].some((field) =>
      field.toLowerCase().includes(normalizedQuery)
    )
  );
}

// Groups sessions by calendar day, preserving the input order
export function groupSessionsByDay(sessions: ScheduleSession[]): DayGroup[] {
  const groups = new Map<string, DayGroup>();

  for (const session of sessions) {
    const key = toDayKey(session.date);
    const existing = groups.get(key);

    if (existing) {
      existing.sessions.push(session);
    } else {
      groups.set(key, { key, date: session.date, sessions: [session] });
    }
  }

  return [...groups.values()];
}