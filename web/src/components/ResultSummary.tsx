import * as React from "react";

import type { ExtractionResponse } from "@/lib/types";
import { Badge } from "@/components/Badge";

type Props = {
  result: ExtractionResponse;
  requestId?: string;
};

export function ResultSummary({ result, requestId }: Props) {
  const isValid = result.validation?.is_valid;
  const errors = result.validation?.errors ?? [];
  const warnings = result.validation?.warnings ?? [];

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">Extraction Result</h2>
          <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
            Status: <span className="font-medium text-zinc-900 dark:text-zinc-50">{result.status}</span>
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          {typeof isValid === "boolean" ? (
            isValid ? (
              <Badge tone="success">Valid</Badge>
            ) : (
              <Badge tone="danger">Invalid</Badge>
            )
          ) : (
            <Badge>Validation n/a</Badge>
          )}
          <Badge tone={errors.length ? "danger" : "neutral"}>Errors: {errors.length}</Badge>
          <Badge tone={warnings.length ? "warning" : "neutral"}>Warnings: {warnings.length}</Badge>
        </div>
      </div>

      <dl className="mt-4 grid grid-cols-1 gap-3 text-sm sm:grid-cols-3">
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-900">
          <dt className="text-xs text-zinc-500 dark:text-zinc-400">Request ID</dt>
          <dd className="mt-1 truncate font-medium text-zinc-900 dark:text-zinc-50">
            {requestId ?? result.meta.request_id}
          </dd>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-900">
          <dt className="text-xs text-zinc-500 dark:text-zinc-400">Method</dt>
          <dd className="mt-1 font-medium text-zinc-900 dark:text-zinc-50">{result.meta.method}</dd>
        </div>
        <div className="rounded-xl border border-zinc-200 bg-zinc-50 p-3 dark:border-zinc-800 dark:bg-zinc-900">
          <dt className="text-xs text-zinc-500 dark:text-zinc-400">Pages</dt>
          <dd className="mt-1 font-medium text-zinc-900 dark:text-zinc-50">
            {result.meta.page_count ?? "—"}
          </dd>
        </div>
      </dl>
    </section>
  );
}
