import type { ScheduleSession } from "../types/schedule";

interface SessionCardProps {
  session: ScheduleSession;
}

export default function SessionCard({ session }: SessionCardProps) {
  return (
    <article className="session-card">
      <header className="session-card__header">
        <h3 className="session-card__subject">{session.subject}</h3>
        <time className="session-card__time">
          {session.startTime} – {session.endTime}
        </time>
      </header>

      <dl className="session-card__details">
        <div>
          <dt>Aula</dt>
          <dd>{session.location || "Sin aula asignada"}</dd>
        </div>
        {session.description && (
          <div>
            <dt>Detalle</dt>
            <dd>{session.description}</dd>
          </div>
        )}
      </dl>
    </article>
  );
}