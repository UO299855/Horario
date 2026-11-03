import { useMemo } from "react";
import { SCHEDULE_SOURCES, type ScheduleSourceId } from "../config";
import type { CalendarEvent, ScheduleSession } from "../types/schedule";
import { useSchedule, type ScheduleState } from "./useSchedule";

export type CalendarData =
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "ready"; events: CalendarEvent[] };

function getFileName(id: ScheduleSourceId): string {
  const source = SCHEDULE_SOURCES.find((item) => item.id === id);
  if (!source) throw new Error(`Fuente de horario desconocida: ${id}`);
  return source.fileName;
}

function tagSessions(sourceId: ScheduleSourceId, sessions: ScheduleSession[]): CalendarEvent[] {
  return sessions.map((session) => ({ ...session, sourceId }));
}

// Loads both timetables and merges them into one list of events for the calendar
export function useCalendarData(): CalendarData {
  const math = useSchedule(getFileName("math"));
  const software = useSchedule(getFileName("software"));

  return useMemo<CalendarData>(() => {
    const states: ScheduleState[] = [math, software];

    const failed = states.find((state) => state.status === "error");
    if (failed?.status === "error") {
      return { status: "error", message: failed.message };
    }

    if (states.some((state) => state.status === "loading")) {
      return { status: "loading" };
    }

    const events = [
      ...(math.status === "ready" ? tagSessions("math", math.sessions) : []),
      ...(software.status === "ready" ? tagSessions("software", software.sessions) : []),
    ];

    return { status: "ready", events };
  }, [math, software]);
}