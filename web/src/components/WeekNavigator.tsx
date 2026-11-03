import { addDays, addWeeks, startOfWeek } from "../utils/weekUtils";
import { formatWeekRange } from "../utils/dateFormat";

interface WeekNavigatorProps {
  weekStart: Date;
  onChange: (weekStart: Date) => void;
}

export default function WeekNavigator({ weekStart, onChange }: WeekNavigatorProps) {
  const friday = addDays(weekStart, 4);

  return (
    <nav className="week-nav" aria-label="Navegación por semanas">
      <button
        type="button"
        className="week-nav__button"
        onClick={() => onChange(addWeeks(weekStart, -1))}
        aria-label="Semana anterior"
      >
        ‹
      </button>

      <div className="week-nav__center">
        <p className="week-nav__range">{formatWeekRange(weekStart, friday)}</p>
        <button
          type="button"
          className="week-nav__today"
          onClick={() => onChange(startOfWeek(new Date()))}
        >
          Hoy
        </button>
      </div>

      <button
        type="button"
        className="week-nav__button"
        onClick={() => onChange(addWeeks(weekStart, 1))}
        aria-label="Semana siguiente"
      >
        ›
      </button>
    </nav>
  );
}