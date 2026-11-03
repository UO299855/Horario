import { DEFAULT_END_HOUR, DEFAULT_START_HOUR, HOUR_HEIGHT_PX } from "../config";
import type { CalendarEvent } from "../types/schedule";
import { isSameDay, timeToMinutes } from "../utils/weekUtils";

export interface HourRange {
  startHour: number;
  endHour: number;
}

export interface PlacedEvent {
  event: CalendarEvent;
  lane: number;
  laneCount: number;
}

export function getEventsForDay(events: CalendarEvent[], day: Date): CalendarEvent[] {
  return events.filter((event) => isSameDay(event.date, day));
}

// Expands the default hour range so every event in the week fits in the grid
export function getHourRange(events: CalendarEvent[]): HourRange {
  let startHour = DEFAULT_START_HOUR;
  let endHour = DEFAULT_END_HOUR;

  for (const event of events) {
    startHour = Math.min(startHour, Math.floor(timeToMinutes(event.startTime) / 60));
    endHour = Math.max(endHour, Math.ceil(timeToMinutes(event.endTime) / 60));
  }

  return { startHour, endHour };
}

// Places overlapping events of the same day in separate lanes, side by side
export function layoutDayEvents(dayEvents: CalendarEvent[]): PlacedEvent[] {
  const sorted = [...dayEvents].sort(
    (a, b) => timeToMinutes(a.startTime) - timeToMinutes(b.startTime)
  );

  // Each lane stores the end time of the last event placed in it
  const laneEnds: number[] = [];
  const placed = sorted.map((event) => {
    const start = timeToMinutes(event.startTime);
    const end = timeToMinutes(event.endTime);

    let lane = laneEnds.findIndex((laneEnd) => laneEnd <= start);
    if (lane === -1) {
      lane = laneEnds.length;
      laneEnds.push(end);
    } else {
      laneEnds[lane] = end;
    }

    return { event, lane };
  });

  const laneCount = Math.max(1, laneEnds.length);
  return placed.map((item) => ({ ...item, laneCount }));
}

// Vertical position and height of an event, in pixels, relative to the grid's first hour
export function getEventBox(event: CalendarEvent, startHour: number): { top: number; height: number } {
  const start = timeToMinutes(event.startTime);
  const end = timeToMinutes(event.endTime);

  return {
    top: ((start - startHour * 60) / 60) * HOUR_HEIGHT_PX,
    height: ((end - start) / 60) * HOUR_HEIGHT_PX,
  };
}