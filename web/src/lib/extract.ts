import type { ExtractionResponse, JobCreateResponse, JobGetResponse, JobStatus } from "@/lib/types";

export type ExtractOptions = {
  schemaName: string;
  file: File;
};

export type StartExtractOptions = ExtractOptions & {
  asyncMode?: boolean;
};

export type StartExtractResult =
  | {
      mode: "sync";
      response: ExtractionResponse;
      requestId?: string;
    }
  | {
      mode: "async";
      jobId: string;
      status: JobStatus;
    };

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function startExtraction({ schemaName, file, asyncMode }: StartExtractOptions): Promise<StartExtractResult> {
  const form = new FormData();
  form.append("schema_name", schemaName);
  form.append("file", file);

  const r = await fetch(`/api/extractions${asyncMode ? "?async_mode=true" : ""}`,
  {
    method: "POST",
    body: form,
  });

  const requestId = r.headers.get("x-request-id") ?? undefined;
  const json = (await r.json()) as unknown;

  if (!r.ok) {
    const message = (json as { detail?: string }).detail;
    throw new Error(message ?? `Request failed (${r.status})`);
  }

  if (r.status === 202) {
    const body = json as JobCreateResponse;
    return { mode: "async", jobId: body.job_id, status: body.status };
  }

  return { mode: "sync", response: json as ExtractionResponse, requestId };
}

export async function getExtractionJob(jobId: string): Promise<JobGetResponse> {
  const r = await fetch(`/api/extractions/${encodeURIComponent(jobId)}`, {
    method: "GET",
    cache: "no-store",
  });

  const json = (await r.json()) as unknown;
  if (!r.ok) {
    const message = (json as { detail?: string }).detail;
    throw new Error(message ?? `Request failed (${r.status})`);
  }

  return json as JobGetResponse;
}

export async function pollExtractionJob(
  jobId: string,
  opts?: {
    timeoutMs?: number;
    intervalMs?: number;
    onStatus?: (status: JobStatus) => void;
  },
): Promise<ExtractionResponse> {
  const timeoutMs = opts?.timeoutMs ?? 25_000;
  const intervalMs = opts?.intervalMs ?? 750;
  const start = Date.now();

  for (;;) {
    const rec = await getExtractionJob(jobId);
    opts?.onStatus?.(rec.status);

    if (rec.status === "failed") {
      throw new Error(rec.error ?? "Job failed");
    }

    if (rec.status === "completed") {
      if (!rec.result) {
        throw new Error("Job completed but result is empty");
      }
      return rec.result;
    }

    if (Date.now() - start > timeoutMs) {
      throw new Error("Timed out waiting for extraction job");
    }

    await sleep(intervalMs);
  }
}

export async function checkBackend(): Promise<{
  ok: boolean;
  backendUrl: string;
  status: number;
}> {
  const r = await fetch("/api/health", { cache: "no-store" });
  const json = (await r.json()) as {
    ok: boolean;
    backendUrl: string;
    status: number;
  };

  return json;
}
