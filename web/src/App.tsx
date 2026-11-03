import ScheduleCalendar from "./components/ScheduleCalendar";
import CalendarLegend from "./components/CalendarLegend";

export default function App() {
  return (
    <div className="app">
      <header className="app__header">
        <h1 className="app__title">Mi horario</h1>
        <CalendarLegend />
      </header>

      <main className="app__main">
        <ScheduleCalendar />
      </main>
    </div>
  );
}