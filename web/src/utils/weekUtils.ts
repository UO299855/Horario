export const WORKING_DAYS = 5;

// Returns a new date shifted by a number of days, at local midnight
export function addDays(date: Date, days: number): Date {
  return new Date(date.getFullYear(), date.getMonth(), date.getDate() + days);
}

export function addWeeks(date: Date, weeks: number): Date {
  return addDays(date, weeks * 7);
}

// Returns the Monday of the week containing `date`, at local midnight
export function startOfWeek(date: Date): Date {
  const midnight = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  const daysSinceMonday = (midnight.getDay() + 6) % 7;
  return addDays(midnight, -daysSinceMonday);
}

// Returns Monday through Friday of the week starting at `monday`
export function getWeekDays(monday: Date): Date[] {
  return Array.from({ length: WORKING_DAYS }, (_, index) => addDays(monday, index));
}

export function isSameDay(a: Date, b: Date): boolean {
  return (
    a.getFullYear() === b.getFullYear() &&
    a.getMonth() === b.getMonth() &&
    a.getDate() === b.getDate()
  );
}

// "09:30" -> 570
export function timeToMinutes(time: string): number {
  const [hours, minutes] = time.split(":").map(Number);
  return hours * 60 + minutes;
}