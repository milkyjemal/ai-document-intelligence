import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function getBackendUrl(): string {
  return process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
}

export async function POST(req: Request) {
  const backendUrl = getBackendUrl();
  const url = new URL(req.url);

  let incoming: FormData;
  try {
    incoming = await req.formData();
  } catch {
    return NextResponse.json({ error: "Invalid multipart form data" }, { status: 400 });
  }

  const outgoing = new FormData();
  for (const [key, value] of incoming.entries()) {
    outgoing.append(key, value);
  }

  let upstream: Response;
  try {
    upstream = await fetch(`${backendUrl}/v1/extractions${url.search}`, {
      method: "POST",
      body: outgoing,
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json(
      { error: "Failed to reach backend", detail: message, backendUrl },
      { status: 502 },
    );
  }

  const contentType = upstream.headers.get("content-type") ?? "";
  const requestId = upstream.headers.get("x-request-id") ?? undefined;
  const jobId = upstream.headers.get("x-job-id") ?? undefined;
  const headers = {
    ...(requestId ? { "x-request-id": requestId } : {}),
    ...(jobId ? { "x-job-id": jobId } : {}),
  };

  if (contentType.includes("application/json")) {
    const json = await upstream.json().catch(() => null);
    return NextResponse.json(json, {
      status: upstream.status,
      headers: Object.keys(headers).length ? headers : undefined,
    });
  }

  const text = await upstream.text().catch(() => "");
  return NextResponse.json(
    { error: "Unexpected backend response", status: upstream.status, body: text },
    {
      status: 502,
      headers: Object.keys(headers).length ? headers : undefined,
    },
  );
}
