"use client";

import { useEffect, useState } from "react";
import type { AgentRunEvent } from "@/lib/types";

const EVENT_TYPES = [
  "run.created",
  "run.state_changed",
  "run.output_generated",
  "tool.allowed",
  "tool.denied",
] as const;

function eventLabel(event: AgentRunEvent): string {
  if (event.event_type === "run.state_changed") {
    return `${event.from_state ?? "start"} → ${event.to_state ?? "unknown"}`;
  }
  if (event.event_type === "run.output_generated") return "Output generated";
  if (event.event_type === "run.created") return "Run created";
  if (event.event_type === "tool.allowed") return "Tool request allowed";
  if (event.event_type === "tool.denied") return "Tool request denied";
  return event.message ?? event.event_type.replaceAll(".", " ");
}

export default function AgentRunTrace({ runId }: { runId: string }) {
  const [open, setOpen] = useState(false);
  const [status, setStatus] = useState<"idle" | "connecting" | "live" | "reconnecting">("idle");
  const [events, setEvents] = useState<AgentRunEvent[]>([]);

  useEffect(() => {
    if (!open) return;

    const source = new EventSource(`/api/agent-runs/${runId}/events/stream`);
    const handleEvent = (raw: Event) => {
      if (!(raw instanceof MessageEvent) || typeof raw.data !== "string") return;
      const event = JSON.parse(raw.data) as AgentRunEvent;
      setEvents((current) => {
        if (current.some((item) => item.id === event.id)) return current;
        return [...current, event].sort((left, right) => left.sequence - right.sequence);
      });
      setStatus("live");
    };

    for (const eventType of EVENT_TYPES) source.addEventListener(eventType, handleEvent);
    source.onopen = () => setStatus("live");
    source.onerror = () => setStatus("reconnecting");

    return () => {
      for (const eventType of EVENT_TYPES) source.removeEventListener(eventType, handleEvent);
      source.close();
    };
  }, [open, runId]);

  if (!open) {
    return (
      <button
        className="trace-toggle"
        type="button"
        onClick={() => {
          setStatus("connecting");
          setOpen(true);
        }}
      >
        Open live trace
      </button>
    );
  }

  return (
    <section className="run-trace" aria-label="Agent run trace">
      <div className="run-trace-header">
        <strong>Live trace</strong>
        <span>{status}</span>
        <button
          className="trace-toggle"
          type="button"
          onClick={() => {
            setOpen(false);
            setStatus("idle");
          }}
        >
          Close trace
        </button>
      </div>
      {events.length === 0 ? (
        <p className="card-copy">Waiting for run events…</p>
      ) : (
        <ol className="run-trace-list">
          {events.map((event) => (
            <li key={event.id}>
              <span>Event {event.sequence}</span>
              <strong>{eventLabel(event)}</strong>
              <time dateTime={event.created_at}>{new Date(event.created_at).toLocaleTimeString()}</time>
            </li>
          ))}
        </ol>
      )}
    </section>
  );
}
