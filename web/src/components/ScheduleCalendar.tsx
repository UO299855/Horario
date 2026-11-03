import { useState } from "react";
import { useCalendarData } from "../hooks/useCalendarData";
import { startOfWeek } from "../utils/weekUtils";
import WeekCalendar from "./WeekCalendar";
import WeekNavigator from "./WeekNavigator";

export default function ScheduleCalendar() {
  // The current week is selected by default
  const [weekStart, setWeekStart] = useState(() => startOfWeek(new Date()));
  const calendar = useCalendarData();

  return (
    <section className="schedule">
      <WeekNavigator weekStart={weekStart} onChange={setWeekStart} />

      {calendar.status === "loading" && (
        <p className="status" role="status">Cargando horarios…</p>
      )}

      {calendar.status === "error" && (
        <p className="status status--error" role="alert">
          No se pudieron cargar los horarios. {calendar.message}
        </p>
      )}

      {calendar.status === "ready" && (
        <WeekCalendar weekStart={weekStart} events={calendar.events} />
      )}
    </section>
  );
}