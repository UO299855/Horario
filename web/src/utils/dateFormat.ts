const weekdayFormatter = new Intl.DateTimeFormat("es-ES", { weekday: "short" });
const dateFormatter = new Intl.DateTimeFormat("es-ES", {
  day: "numeric",
  month: "short",
  year: "numeric",
});

// Date -> "Lun" (first letter capitalized, no trailing dot)
export function formatWeekdayLabel(date: Date): string {
  const text = weekdayFormatter.format(date).replace(".", "");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

// Date -> "14"
export function formatDayNumber(date: Date): string {
  return String(date.getDate());
}

// (14 sept 2026, 18 sept 2026) -> "14 sept 2026 – 18 sept 2026"
export function formatWeekRange(from: Date, to: Date): string {
  return `${dateFormatter.format(from)} – ${dateFormatter.format(to)}`;
}