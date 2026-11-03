import type { ScheduleSource, ScheduleSourceId } from "../config";

interface SourceSelectorProps {
  sources: readonly ScheduleSource[];
  activeId: ScheduleSourceId;
  onChange: (id: ScheduleSourceId) => void;
}

export default function SourceSelector({ sources, activeId, onChange }: SourceSelectorProps) {
  return (
    <div className="source-selector" role="tablist" aria-label="Horario">
      {sources.map((source) => {
        const isActive = source.id === activeId;

        return (
          <button
            key={source.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            className="source-selector__tab"
            onClick={() => onChange(source.id)}
          >
            {source.label}
          </button>
        );
      })}
    </div>
  );
}