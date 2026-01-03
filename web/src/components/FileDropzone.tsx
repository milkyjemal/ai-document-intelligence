"use client";

import * as React from "react";

type Props = {
  accept?: string;
  maxBytes?: number;
  file: File | null;
  onChange: (file: File | null) => void;
};

function formatBytes(bytes: number): string {
  const units = ["B", "KB", "MB", "GB"];
  let value = bytes;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(i === 0 ? 0 : 1)} ${units[i]}`;
}

export function FileDropzone({
  accept = "application/pdf",
  maxBytes = 10_000_000,
  file,
  onChange,
}: Props) {
  const inputRef = React.useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);

  function pick() {
    inputRef.current?.click();
  }

  function validate(next: File | null) {
    if (!next) {
      setError(null);
      return true;
    }

    if (accept && next.type && !accept.split(",").includes(next.type)) {
      setError("Only PDF files are supported.");
      return false;
    }

    if (next.size > maxBytes) {
      setError(`File is too large. Max size is ${formatBytes(maxBytes)}.`);
      return false;
    }

    setError(null);
    return true;
  }

  function set(next: File | null) {
    if (!validate(next)) return;
    onChange(next);
  }

  function onInputChange(e: React.ChangeEvent<HTMLInputElement>) {
    const f = e.target.files?.[0] ?? null;
    set(f);
  }

  function onDrop(e: React.DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setIsDragging(false);
    const f = e.dataTransfer.files?.[0] ?? null;
    set(f);
  }

  return (
    <div>
      <div
        onClick={pick}
        onDragOver={(e) => {
          e.preventDefault();
          setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={`group relative cursor-pointer rounded-2xl border bg-white p-6 shadow-sm transition dark:bg-zinc-950 ${
          isDragging
            ? "border-zinc-900 ring-4 ring-zinc-900/10 dark:border-zinc-200 dark:ring-zinc-200/10"
            : "border-zinc-200 hover:border-zinc-300 dark:border-zinc-800 dark:hover:border-zinc-700"
        }`}
        role="button"
        tabIndex={0}
      >
        <input
          ref={inputRef}
          type="file"
          accept={accept}
          onChange={onInputChange}
          className="hidden"
        />

        <div className="flex items-start justify-between gap-6">
          <div>
            <h2 className="text-base font-semibold text-zinc-900 dark:text-zinc-50">
              Upload a Bill of Lading (PDF)
            </h2>
            <p className="mt-1 text-sm text-zinc-600 dark:text-zinc-400">
              Drag and drop a PDF here, or click to browse.
            </p>
            <p className="mt-3 text-xs text-zinc-500 dark:text-zinc-500">
              Max size: {formatBytes(maxBytes)}
            </p>
          </div>

          <div className="shrink-0 rounded-xl border border-zinc-200 bg-zinc-50 px-3 py-2 text-xs font-medium text-zinc-900 group-hover:bg-zinc-100 dark:border-zinc-800 dark:bg-zinc-900 dark:text-zinc-100 dark:group-hover:bg-zinc-800">
            Choose file
          </div>
        </div>

        <div className="mt-4 rounded-xl border border-zinc-200 bg-zinc-50 p-4 dark:border-zinc-800 dark:bg-zinc-900">
          {file ? (
            <div className="flex items-center justify-between gap-4">
              <div className="min-w-0">
                <p className="truncate text-sm font-medium text-zinc-900 dark:text-zinc-50">
                  {file.name}
                </p>
                <p className="text-xs text-zinc-600 dark:text-zinc-400">
                  {formatBytes(file.size)}
                </p>
              </div>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  onChange(null);
                  setError(null);
                  if (inputRef.current) inputRef.current.value = "";
                }}
                className="rounded-lg border border-zinc-200 bg-white px-3 py-2 text-xs font-medium text-zinc-900 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
              >
                Remove
              </button>
            </div>
          ) : (
            <p className="text-sm text-zinc-600 dark:text-zinc-400">No file selected.</p>
          )}
        </div>
      </div>

      {error ? (
        <p className="mt-3 text-sm text-rose-700 dark:text-rose-300">{error}</p>
      ) : null}
    </div>
  );
}
