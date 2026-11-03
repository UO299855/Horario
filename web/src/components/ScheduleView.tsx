import { useMemo, useState } from "react";
import { useSchedule } from "../hooks/useSchedule";
import { filterSessions, groupSessionsByDay } from "../domain/scheduleGrouping";
import DayGroupSection from "./DayGroup";
import ScheduleSearch from "./ScheduleSearch";

interface ScheduleViewProps {
  fileName: string;
}

export default function ScheduleView({ fileName }: ScheduleViewProps) {
  const schedule = useSchedule(fileName);
  const [query, setQuery] = useState("");

  const sessions = schedule.status === "ready" ? schedule.sessions : [];
  const dayGroups = useMemo(
    () => groupSessionsByDay(filterSessions(sessions, query)),
    [sessions, query]
  );

  if (schedule.status === "loading") {
    return <p className="status" role="status">Cargando horario…</p>;
  }

  if (schedule.status === "error") {
    return (
      <p className="status status--error" role="alert">
        No se pudo cargar el horario. {schedule.message}
      </p>
    );
  }

  return (
    <section className="schedule">
      <ScheduleSearch value={query} onChange={setQuery} />

      {dayGroups.length === 0 ? (
        <p className="status">No hay clases que coincidan con la búsqueda.</p>
      ) : (
        dayGroups.map((group) => <DayGroupSection key={group.key} group={group} />)
      )}
    </section>
  );
}