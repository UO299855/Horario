import { getEventBox } from "../domain/weekLayout";
import type { CalendarEvent } from "../types/schedule";

interface CalendarEventBlockProps {
  event: CalendarEvent;
  startHour: number;
  lane: number;
  laneCount: number;
}

export default function CalendarEventBlock({ event, startHour, lane, laneCount }: CalendarEventBlockProps) {
  const { top, height } = getEventBox(event, startHour);
  const laneWidth = 100 / laneCount;

  // Full details go in the tooltip, since small blocks cannot show everything
  const tooltip = [event.subject, `${event.startTime}–${event.endTime}`, event.location, event.description]
    .filter(Boolean)
    .join("\n");

  return (
    <article
      className={`calendar-event calendar-event--${event.sourceId}`}
      style={{
        top,
        height,
        left: `calc(${lane * laneWidth}% + 2px)`,
        width: `calc(${laneWidth}% - 4px)`,
      }}
      title={tooltip}
    >
      <p className="calendar-event__subject">{event.subject}</p>
      <p className="calendar-event__meta">
        {event.startTime}–{event.endTime}
      </p>
      {event.location && <p className="calendar-event__meta">{event.location}</p>}
    </article>
  );
}