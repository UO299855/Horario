import { useMemo } from "react";
import { HOUR_HEIGHT_PX } from "../config";
import { getEventsForDay, getHourRange, layoutDayEvents } from "../domain/weekLayout";
import { formatDayNumber, formatWeekdayLabel } from "../utils/dateFormat";
import { getWeekDays, isSameDay } from "../utils/weekUtils";
import type { CalendarEvent } from "../types/schedule";
import CalendarEventBlock from "./CalendarEventBlock";

interface WeekCalendarProps {
  weekStart: Date;
  events: CalendarEvent[];
}

export default function WeekCalendar({ weekStart, events }: WeekCalendarProps) {
  const days = useMemo(() => getWeekDays(weekStart), [weekStart]);

  const weekEvents = useMemo(
    () => events.filter((event) => days.some((day) => isSameDay(day, event.date))),
    [events, days]
  );

  const { startHour, endHour } = useMemo(() => getHourRange(weekEvents), [weekEvents]);
  const hours = Array.from({ length: endHour - startHour }, (_, index) => startHour + index);
  const gridHeight = hours.length * HOUR_HEIGHT_PX;

  return (
    <div className="calendar">
      <div className="calendar__scroll">
        <div
          className="calendar__grid"
          style={{ gridTemplateColumns: `3.5rem repeat(${days.length}, minmax(0, 1fr))` }}
        >
          {/* First row: corner and day headers */}
          <div className="calendar__corner" />
          {days.map((day) => (
            <div key={day.toISOString()} className="calendar__day-header">
              <span className="calendar__weekday">{formatWeekdayLabel(day)}</span>
              <span className="calendar__date">{formatDayNumber(day)}</span>
            </div>
          ))}

          {/* Second row: hour labels, then one column per day */}
          <div className="calendar__times" style={{ height: gridHeight }}>
            {hours.map((hour) => (
              <span
                key={hour}
                className="calendar__hour-label"
                style={{ top: (hour - startHour) * HOUR_HEIGHT_PX }}
              >
                {String(hour).padStart(2, "0")}:00
              </span>
            ))}
          </div>

          {days.map((day) => {
            const placedEvents = layoutDayEvents(getEventsForDay(weekEvents, day));

            return (
              <div key={day.toISOString()} className="calendar__column" style={{ height: gridHeight }}>
                {hours.map((hour) => (
                  <div
                    key={hour}
                    className="calendar__hour-line"
                    style={{ top: (hour - startHour) * HOUR_HEIGHT_PX }}
                  />
                ))}

                {placedEvents.map(({ event, lane, laneCount }) => (
                  <CalendarEventBlock
                    key={`${event.sourceId}-${event.id}`}
                    event={event}
                    startHour={startHour}
                    lane={lane}
                    laneCount={laneCount}
                  />
                ))}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}