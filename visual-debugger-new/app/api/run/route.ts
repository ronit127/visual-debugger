import { NextResponse } from "next/server";

const FLASK_URL = process.env.FLASK_API_URL || "http://localhost:5000/api/run";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const res = await fetch(FLASK_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    const data = await res.json();
    return NextResponse.json(data, { status: res.status });
  } catch (err: any) {
    const message = err?.message || "Failed to reach backend";
    return NextResponse.json({ status: "error", error: message }, { status: 500 });
  }
}
