"use client";

import React, { useMemo, useState } from "react";
import CodeEditor from "./components/editor";
import DraggableComponent from "./components/draggable";
import GraphPanel from "./components/GraphPanel";
import ListPanel from "./components/ListPanel";
import HeapPanel from "./components/HeapPanel";
import DictPanel from "./components/DictPanel";
import LogPanel from "./components/LogPanel";
import { RunResponse, BackendStructure } from "./types/backend";

type PanelKind = BackendStructure["type"] | "log" | "output";

interface PanelState {
  id: string;
  title: string;
  kind: PanelKind;
  payload: any;
  operations?: string[];
  size: { width: number; height: number };
}

export default function App() {
  const [code, setCode] = useState<string>(
    `# Welcome to Visual Debugger\n# Paste Python code and click Run\n`
  );
  const [panels, setPanels] = useState<PanelState[]>([]);
  const [output, setOutput] = useState<string>("");
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [zCounter, setZCounter] = useState(20);
  const [zMap, setZMap] = useState<Record<string, number>>({});

  const handleChange = (value: string) => {
    setCode(value ?? "");
  };

  const renderPanelContent = (panel: PanelState) => {
    const varName = panel.title.split(": ")[1];
    switch (panel.kind) {
      case "graph":
        return (
          <GraphPanel
            data={panel.payload}
            width={panel.size.width - 24}
            height={panel.size.height - 100}
          />
        );
      case "list":
        return <ListPanel name={varName} values={panel.payload || []} />;
      case "heap":
        return <HeapPanel name={varName} values={panel.payload || []} operations={panel.operations} />;
      case "dict":
        return <DictPanel name={varName} entries={panel.payload || {}} />;
      case "log":
        return <LogPanel title={panel.title} lines={panel.payload || []} />;
      default:
        return (
          <pre className="h-full w-full overflow-auto bg-gray-900 p-3 font-mono text-xs text-green-200">
            {JSON.stringify(panel.payload, null, 2)}
          </pre>
        );
    }
  };

  const runCode = async () => {
    setIsRunning(true);
    setError(null);
    try {
      const res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });

      const data: RunResponse = await res.json();
      if (!res.ok) {
        throw new Error(data?.error || "Backend error");
      }

      setOutput(data.output || "");

      const nextPanels: PanelState[] = [];

      if (Array.isArray(data.structures)) {
        data.structures.forEach((s, idx) => {
          const typeLabel = s.type.charAt(0).toUpperCase() + s.type.slice(1);
          
          // Calculate dynamic size based on structure type and content
          let width = 400;
          let height = 300;
          
          if (s.type === "graph") {
            const nodeCount = s.payload?.nodes?.length || 0;
            width = Math.max(400, Math.min(800, nodeCount * 80 + 200));
            height = Math.max(350, Math.min(600, nodeCount * 60 + 150));
          } else if (s.type === "list") {
            const itemCount = s.payload?.length || 0;
            height = Math.max(200, Math.min(500, itemCount * 40 + 150));
            width = 350;
          } else if (s.type === "heap") {
            const itemCount = s.payload?.length || 0;
            height = Math.max(250, Math.min(450, Math.ceil(itemCount / 4) * 60 + 150));
            width = 400;
          } else if (s.type === "dict") {
            const keyCount = Object.keys(s.payload || {}).length;
            height = Math.max(250, Math.min(500, keyCount * 50 + 150));
            width = 400;
          }

          nextPanels.push({
            id: `struct-${idx}-${s.name}`,
            title: `${typeLabel}: ${s.name}`,
            kind: s.type,
            payload: s.payload,
            operations: s.operations,
            size: { width, height },
          });
        });
      }

      setPanels(nextPanels);
      // seed z-order
      setZMap(() => {
        const base: Record<string, number> = {};
        let counter = 30;
        nextPanels.forEach((p) => {
          counter += 1;
          base[p.id] = counter;
        });
        setZCounter(counter);
        return base;
      });
      setActiveId(nextPanels[0]?.id ?? null);
    } catch (err: any) {
      setError(err?.message || "Failed to run code");
    } finally {
      setIsRunning(false);
    }
  };

  const draggablePanels = useMemo(() => panels, [panels]);

  const focusPanel = (id: string) => {
    setActiveId(id);
    setZCounter((prev) => {
      const next = prev + 1;
      setZMap((m) => ({ ...m, [id]: next }));
      return next;
    });
  };

  const switchFocus = () => {
    if (!panels.length) return;
    const ids = panels.map((p) => p.id);
    const currentIdx = activeId ? ids.indexOf(activeId) : -1;
    const nextIdx = (currentIdx + 1) % ids.length;
    focusPanel(ids[nextIdx]);
  };

  const closePanel = (id: string) => {
    setPanels((prev) => prev.filter((p) => p.id !== id));
    if (activeId === id) {
      setActiveId(panels.find((p) => p.id !== id)?.id ?? null);
    }
  };

  return (
    <div className="relative min-h-screen w-full bg-zinc-100">
      {/* Full-width header bar */}
        {/* Header slightly wider than main content (20% wider than max-w-6xl) */}
        <div className="mx-auto wide-header px-5 py-5 bg-white rounded-xl shadow-sm">
            <header className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-semibold text-zinc-900">Visual Debugger</h1>
              </div>
            <div className="flex items-center gap-3">
              <button
                className="btn-avant primary"
                onClick={runCode}
                disabled={isRunning}
                aria-label="Run code"
              >
                <svg
                  className="w-4 h-4"
                  viewBox="0 0 24 24"
                  fill="none"
                  xmlns="http://www.w3.org/2000/svg"
                  aria-hidden="true"
                >
                  <path d="M5 3v18l15-9L5 3z" fill="currentColor" />
                </svg>
                <span>{isRunning ? "Running..." : "Run Code"}</span>
              </button>
              <button
                className="btn-avant secondary"
                onClick={runCode}
                disabled={true}
              >
                {"Debug"}
              </button>
            </div>
          </header>
        </div>

      <div className="mx-auto max-w-6xl px-6 py-8">
        <div className="flex flex-col md:flex-row gap-6">
          <div className="md:w-2/3">
            <div className="card w-full overflow-hidden rounded-xl border border-zinc-200 bg-white shadow">
                <div className="mb-0 px-2 text-xs uppercase text-gray-500">Editor</div>
                <CodeEditor code={code} onChange={handleChange} height="70vh" zIndex={10} />
              </div>
          </div>

          <div className="md:w-1/3">
            <div className="card rounded-lg border border-zinc-200 bg-white p-4 text-sm text-gray-800 h-[70vh] overflow-auto">
              <div className="mb-2 text-xs uppercase text-gray-500">Program Output</div>
              <pre className="font-mono text-xs text-gray-900">{output || "(no output)"}</pre>
              {error && <div className="mt-2 text-xs text-red-600">Error: {error}</div>}
            </div>
          </div>
        </div>
      </div>

      {/* Floating panels */}
      {draggablePanels.map((panel, idx) => (
        <DraggableComponent
          key={panel.id}
          id={panel.id}
          title={panel.title}
          defaultX={80 + idx * 40}
          defaultY={100 + idx * 30}
          defaultWidth={panel.size.width}
          defaultHeight={panel.size.height}
          zIndex={zMap[panel.id] ?? 10 + idx}
          onFocus={focusPanel}
          onClose={closePanel}
          isActive={activeId === panel.id}
        >
          {renderPanelContent(panel)}
        </DraggableComponent>
      ))}
    </div>
  );
}
