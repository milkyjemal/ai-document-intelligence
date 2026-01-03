import type { ExtractionResponse } from "@/lib/types";

export type ExtractOptions = {
  schemaName: string;
  file: File;
};

export async function extractDocument({ schemaName, file }: ExtractOptions): Promise<{
  response: ExtractionResponse;
  requestId?: string;
}> {
  const form = new FormData();
  form.append("schema_name", schemaName);
  form.append("file", file);

  const r = await fetch("/api/extractions", {
    method: "POST",
    body: form,
  });

  const requestId = r.headers.get("x-request-id") ?? undefined;
  const json = (await r.json()) as ExtractionResponse;

  if (!r.ok) {
    const message = (json as unknown as { detail?: string }).detail;
    throw new Error(message ?? `Request failed (${r.status})`);
  }

  return { response: json, requestId };
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
