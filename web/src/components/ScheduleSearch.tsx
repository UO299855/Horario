interface ScheduleSearchProps {
  value: string;
  onChange: (value: string) => void;
}

export default function ScheduleSearch({ value, onChange }: ScheduleSearchProps) {
  return (
    <div className="schedule-search">
      <label className="visually-hidden" htmlFor="schedule-search-input">
        Buscar clases
      </label>
      <input
        id="schedule-search-input"
        type="search"
        placeholder="Buscar por asignatura, aula o descripción…"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      />
    </div>
  );
}