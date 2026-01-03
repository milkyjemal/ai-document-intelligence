"use client";

import * as React from "react";

import type { ExtractionResponse } from "@/lib/types";
import { extractDocument } from "@/lib/extract";
import { TopBar } from "@/components/TopBar";
import { FileDropzone } from "@/components/FileDropzone";
import { PrimaryButton } from "@/components/PrimaryButton";
import { SecondaryButton } from "@/components/SecondaryButton";
import { ResultSummary } from "@/components/ResultSummary";
import { AlertList } from "@/components/AlertList";
import { JsonPanel } from "@/components/JsonPanel";
import { SectionHeading } from "@/components/SectionHeading";

type Tab = "extracted" | "meta" | "raw";

export default function Home() {
  const [schemaName, setSchemaName] = React.useState("bol_v1");
  const [file, setFile] = React.useState<File | null>(null);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState<string | null>(null);
  const [result, setResult] = React.useState<ExtractionResponse | null>(null);
  const [requestId, setRequestId] = React.useState<string | undefined>(undefined);
  const [tab, setTab] = React.useState<Tab>("extracted");

  async function run() {
    if (!file) {
      setError("Please choose a PDF file first.");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);
    setRequestId(undefined);
    setTab("extracted");

    try {
      const r = await extractDocument({ schemaName, file });
      setResult(r.response);
      setRequestId(r.requestId);
    } catch (e) {
      const message = e instanceof Error ? e.message : "Request failed";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  function reset() {
    setError(null);
    setResult(null);
    setRequestId(undefined);
    setTab("extracted");
  }

  const errors = result?.validation?.errors ?? [];
  const warnings = result?.validation?.warnings ?? [];

  return (
    <div className="min-h-full bg-gradient-to-b from-zinc-50 to-white dark:from-black dark:to-black">
      <TopBar />

      <main className="mx-auto w-full max-w-6xl px-6 py-10">
        <div className="grid grid-cols-1 gap-8 lg:grid-cols-5">
          <section className="lg:col-span-2">
            <SectionHeading
              title="New extraction"
              description="Upload a PDF and generate structured JSON. Validation errors/warnings are returned alongside the result."
            />

            <div className="mt-6 space-y-6">
              <div className="rounded-2xl border border-zinc-200 bg-white p-5 shadow-sm dark:border-zinc-800 dark:bg-zinc-950">
                <label className="text-sm font-semibold text-zinc-900 dark:text-zinc-50">
                  Schema
                </label>
                <p className="mt-1 text-xs text-zinc-500 dark:text-zinc-400">
                  Currently supported: bol_v1
                </p>
                <select
                  value={schemaName}
                  onChange={(e) => setSchemaName(e.target.value)}
                  className="mt-3 w-full rounded-xl border border-zinc-200 bg-white px-3 py-2 text-sm text-zinc-900 shadow-sm outline-none ring-0 focus:border-zinc-400 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:focus:border-zinc-600"
                >
                  <option value="bol_v1">bol_v1</option>
                </select>
              </div>

              <FileDropzone file={file} onChange={setFile} />

              <div className="flex flex-wrap gap-3">
                <PrimaryButton loading={loading} onClick={run}>
                  Extract
                </PrimaryButton>
                <SecondaryButton
                  type="button"
                  onClick={() => {
                    setFile(null);
                    reset();
                  }}
                >
                  Clear
                </SecondaryButton>
              </div>

              {error ? (
                <div className="rounded-2xl border border-rose-200 bg-rose-50 p-4 text-sm text-rose-950 dark:border-rose-950/60 dark:bg-rose-950/30 dark:text-rose-100">
                  <p className="font-semibold">Request failed</p>
                  <p className="mt-1">{error}</p>
                </div>
              ) : null}
            </div>
          </section>

          <section className="lg:col-span-3">
            <SectionHeading
              title="Results"
              description="View extracted fields, validation output, and raw response payload."
              right={
                result ? (
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => setTab("extracted")}
                      className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
                        tab === "extracted"
                          ? "bg-zinc-900 text-white dark:bg-zinc-50 dark:text-zinc-950"
                          : "border border-zinc-200 bg-white text-zinc-900 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
                      }`}
                    >
                      Extracted
                    </button>
                    <button
                      type="button"
                      onClick={() => setTab("meta")}
                      className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
                        tab === "meta"
                          ? "bg-zinc-900 text-white dark:bg-zinc-50 dark:text-zinc-950"
                          : "border border-zinc-200 bg-white text-zinc-900 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
                      }`}
                    >
                      Meta
                    </button>
                    <button
                      type="button"
                      onClick={() => setTab("raw")}
                      className={`rounded-xl px-3 py-2 text-sm font-semibold transition ${
                        tab === "raw"
                          ? "bg-zinc-900 text-white dark:bg-zinc-50 dark:text-zinc-950"
                          : "border border-zinc-200 bg-white text-zinc-900 hover:bg-zinc-50 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-50 dark:hover:bg-zinc-900"
                      }`}
                    >
                      Raw
                    </button>
                  </div>
                ) : null
              }
            />

            <div className="mt-6 space-y-6">
              {!result ? (
                <div className="rounded-2xl border border-dashed border-zinc-300 bg-white p-10 text-center text-sm text-zinc-600 dark:border-zinc-800 dark:bg-zinc-950 dark:text-zinc-400">
                  Submit a PDF to see results.
                </div>
              ) : (
                <>
                  <ResultSummary result={result} requestId={requestId} />

                  <div className="grid grid-cols-1 gap-4">
                    <AlertList title="Errors" tone="danger" items={errors} />
                    <AlertList title="Warnings" tone="warning" items={warnings} />
                  </div>

                  {tab === "extracted" ? (
                    <JsonPanel
                      title="Extracted data"
                      subtitle="Validated, structured JSON extracted from the document"
                      value={result.data}
                    />
                  ) : null}

                  {tab === "meta" ? (
                    <JsonPanel
                      title="Meta"
                      subtitle="Request identifiers, method, page count, and timings"
                      value={result.meta}
                    />
                  ) : null}

                  {tab === "raw" ? (
                    <JsonPanel title="Full response" subtitle="Entire response payload" value={result} />
                  ) : null}
                </>
              )}
            </div>
          </section>
        </div>

        <footer className="mt-14 border-t border-zinc-200 pt-6 text-xs text-zinc-500 dark:border-zinc-800 dark:text-zinc-500">
          <p>
            Tip: set <span className="font-mono">BACKEND_URL</span> in
            <span className="font-mono"> web/.env.local</span> to point to your FastAPI server.
          </p>
        </footer>
      </main>
    </div>
  );
}
