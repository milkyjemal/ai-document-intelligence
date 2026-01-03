"use client";

import * as React from "react";
import { Badge } from "@/components/Badge";
import { checkBackend } from "@/lib/extract";

export function TopBar() {
  const [status, setStatus] = React.useState<
    | { state: "loading" }
    | { state: "ok"; backendUrl: string }
    | { state: "down"; backendUrl?: string }
  >({ state: "loading" });

  React.useEffect(() => {
    let canceled = false;

    async function run() {
      try {
        const r = await checkBackend();
        if (canceled) return;
        setStatus(r.ok ? { state: "ok", backendUrl: r.backendUrl } : { state: "down", backendUrl: r.backendUrl });
      } catch {
        if (canceled) return;
        setStatus({ state: "down" });
      }
    }

    run();
    const t = setInterval(run, 10_000);
    return () => {
      canceled = true;
      clearInterval(t);
    };
  }, []);

  return (
    <header className="sticky top-0 z-20 border-b border-zinc-200 bg-white/80 backdrop-blur dark:border-zinc-800 dark:bg-zinc-950/60">
      <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-6 py-4">
        <div className="min-w-0">
          <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">AI Document Intelligence</p>
          <p className="truncate text-xs text-zinc-600 dark:text-zinc-400">
            Upload a PDF Bill of Lading and get structured JSON with validation.
          </p>
        </div>

        <div className="flex items-center gap-2">
          {status.state === "loading" ? <Badge>Checking API…</Badge> : null}
          {status.state === "ok" ? (
            <Badge tone="success">Backend OK</Badge>
          ) : status.state === "down" ? (
            <Badge tone="danger">Backend unreachable</Badge>
          ) : null}

          {status.state !== "loading" ? (
            <span className="hidden max-w-[360px] truncate text-xs text-zinc-500 dark:text-zinc-500 sm:inline">
              {status.backendUrl ? status.backendUrl : "BACKEND_URL not set"}
            </span>
          ) : null}
        </div>
      </div>
    </header>
  );
}
