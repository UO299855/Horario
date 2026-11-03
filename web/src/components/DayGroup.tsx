import type { DayGroup as DayGroupData } from "../types/schedule";
import { formatDayLabel } from "../utils/dateFormat";
import SessionCard from "./SessionCard";

interface DayGroupProps {
  group: DayGroupData;
}

export default function DayGroup({ group }: DayGroupProps) {
  const titleId = `day-${group.key}`;

  return (
    <section className="day-group" aria-labelledby={titleId}>
      <h2 className="day-group__title" id={titleId}>
        {formatDayLabel(group.date)}
      </h2>

      <ul className="session-list">
        {group.sessions.map((session) => (
          <li key={session.id}>
            <SessionCard session={session} />
          </li>
        ))}
      </ul>
    </section>
  );
}