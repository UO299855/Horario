import { useEffect, useState } from "react";
import { fetchScheduleCsv } from "../services/scheduleApi";
import { parseScheduleCsv } from "../domain/scheduleParser";
import type { ScheduleSession } from "../types/schedule";

// A discriminated union: each status carries only the data it needs
export type ScheduleState =
  | { status: "loading" }
  | { status: "ready"; sessions: ScheduleSession[] }
  | { status: "error"; message: string };

// Loads and parses a schedule file, cancelling the request if the file changes or the component unmounts
export function useSchedule(fileName: string): ScheduleState {
  const [state, setState] = useState<ScheduleState>({ status: "loading" });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: "loading" });

    fetchScheduleCsv(fileName, controller.signal)
      .then((csvText) => setState({ status: "ready", sessions: parseScheduleCsv(csvText) }))
      .catch((error: unknown) => {
        if (error instanceof Error && error.name === "AbortError") return;
        const message = error instanceof Error ? error.message : "Error desconocido.";
        setState({ status: "error", message });
      });

    return () => controller.abort();
  }, [fileName]);

  return state;
}