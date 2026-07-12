import { act, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AgentRunTrace from "./agent-run-trace";

class FakeEventSource {
  static latest: FakeEventSource | null = null;
  readonly url: string;
  closed = false;
  onopen: ((event: Event) => void) | null = null;
  onerror: ((event: Event) => void) | null = null;
  private listeners = new Map<string, EventListener[]>();

  constructor(url: string | URL) {
    this.url = String(url);
    FakeEventSource.latest = this;
  }

  addEventListener(type: string, listener: EventListener): void {
    this.listeners.set(type, [...(this.listeners.get(type) ?? []), listener]);
  }

  removeEventListener(type: string, listener: EventListener): void {
    this.listeners.set(type, (this.listeners.get(type) ?? []).filter((item) => item !== listener));
  }

  emit(type: string, payload: object): void {
    const event = new MessageEvent(type, { data: JSON.stringify(payload) });
    for (const listener of this.listeners.get(type) ?? []) listener(event);
  }

  close(): void {
    this.closed = true;
  }
}

describe("AgentRunTrace", () => {
  beforeEach(() => {
    FakeEventSource.latest = null;
    vi.stubGlobal("EventSource", FakeEventSource);
  });

  it("opens a resumable event stream and renders ordered run events", async () => {
    const user = userEvent.setup();
    const { unmount } = render(<AgentRunTrace runId="run-1" />);

    await user.click(screen.getByRole("button", { name: "Open live trace" }));

    expect(FakeEventSource.latest?.url).toBe("/api/agent-runs/run-1/events/stream");
    act(() => {
      FakeEventSource.latest?.emit("run.state_changed", {
        id: "event-2",
        run_id: "run-1",
        sequence: 2,
        event_type: "run.state_changed",
        from_state: "queued",
        to_state: "running",
        message: null,
        payload: {},
        created_at: "2026-07-13T00:00:00Z",
      });
    });

    expect(screen.getByText("queued → running")).toBeVisible();
    expect(screen.getByText("Event 2")).toBeVisible();

    unmount();
    expect(FakeEventSource.latest?.closed).toBe(true);
  });
});
