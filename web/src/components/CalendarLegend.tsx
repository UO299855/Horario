import { SCHEDULE_SOURCES } from "../config";

export default function CalendarLegend() {
  return (
    <ul className="legend">
      {SCHEDULE_SOURCES.map((source) => (
        <li key={source.id} className="legend__item">
          <span className={`legend__swatch legend__swatch--${source.id}`} aria-hidden="true" />
          {source.label}
        </li>
      ))}
    </ul>
  );
}