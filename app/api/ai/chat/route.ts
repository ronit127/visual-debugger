const FLASK_BASE = process.env.FLASK_API_URL?.replace(/\/api\/run$/, "") || "http://localhost:5000";

export const dynamic = "force-dynamic";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const res = await fetch(`${FLASK_BASE}/api/ai/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    if (!res.body) {
      return new Response(
        `data: ${JSON.stringify({ type: "error", error: "No response body from backend" })}\n\n`,
        { status: 502, headers: { "Content-Type": "text/event-stream" } }
      );
    }

    // Pipe the backend stream through to the client
    const { readable, writable } = new TransformStream();
    const writer = writable.getWriter();
    const reader = res.body.getReader();

    (async () => {
      try {
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          await writer.write(value);
        }
      } catch {
        // stream closed
      } finally {
        writer.close().catch(() => {});
      }
    })();

    return new Response(readable, {
      status: res.status,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache, no-transform",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
      },
    });
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : "Failed to reach backend";
    return new Response(
      `data: ${JSON.stringify({ type: "error", error: message })}\n\n`,
      { status: 500, headers: { "Content-Type": "text/event-stream" } }
    );
  }
}
