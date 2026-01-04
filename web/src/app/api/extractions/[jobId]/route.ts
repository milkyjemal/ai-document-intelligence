import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function getBackendUrl(): string {
  return process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
}

export async function GET(_req: Request, ctx: { params: Promise<{ jobId: string }> }) {
  const backendUrl = getBackendUrl();
  const { jobId } = await ctx.params;

  let upstream: Response;
  try {
    upstream = await fetch(`${backendUrl}/v1/extractions/${encodeURIComponent(jobId)}`, {
      method: "GET",
      headers: { accept: "application/json" },
    });
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json(
      { error: "Failed to reach backend", detail: message, backendUrl },
      { status: 502 },
    );
  }

  const contentType = upstream.headers.get("content-type") ?? "";

  if (contentType.includes("application/json")) {
    const json = await upstream.json().catch(() => null);
    return NextResponse.json(json, { status: upstream.status });
  }

  const text = await upstream.text().catch(() => "");
  return NextResponse.json(
    { error: "Unexpected backend response", status: upstream.status, body: text },
    { status: 502 },
  );
}
