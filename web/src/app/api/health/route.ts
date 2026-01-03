import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

function getBackendUrl(): string {
  return process.env.BACKEND_URL ?? "http://127.0.0.1:8000";
}

export async function GET() {
  const backendUrl = getBackendUrl();

  try {
    const r = await fetch(`${backendUrl}/health`, { cache: "no-store" });
    const json = await r.json().catch(() => null);

    return NextResponse.json(
      {
        ok: r.ok,
        backendUrl,
        status: r.status,
        backend: json,
      },
      { status: r.ok ? 200 : 502 },
    );
  } catch (e) {
    const message = e instanceof Error ? e.message : "Unknown error";
    return NextResponse.json(
      { ok: false, backendUrl, error: "Failed to reach backend", detail: message },
      { status: 502 },
    );
  }
}
