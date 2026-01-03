"use client";

import * as React from "react";

type Props = {
  title: string;
  value: unknown;
  subtitle?: string;
};

export function JsonPanel({ title, value, subtitle }: Props) {
  const text = React.useMemo(() => JSON.stringify(value, null, 2), [value]);

  async function copy() {
    await navigator.clipboard.writeText(text);
  }

  return (
    <section className="rounded-2xl border border-zinc-200 bg-white shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
      <div className="flex items-start justify-between gap-4 border-b border-zinc-200 p-4 dark:border-zinc-800">
        <div>
          <h3 className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">{title}</h3>
          {subtitle ? (
            <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">{subtitle}</p>
          ) : null}
        </div>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center justify-center rounded-lg border border-zinc-200 bg-zinc-50 px-3 py-2 text-xs font-medium text-zinc-900 hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-50 dark:hover:bg-zinc-800"
        >
          Copy
        </button>
      </div>
      <pre className="max-h-[420px] overflow-auto p-4 text-xs leading-5 text-zinc-900 dark:text-zinc-100">
        <code>{text}</code>
      </pre>
    </section>
  );
}
