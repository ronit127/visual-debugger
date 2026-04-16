"use client";

import { useCallback, useState } from "react";
import { PiPlayFill } from "react-icons/pi";
import { TbDotsDiagonal, TbDotsDiagonal2, TbDotsVertical } from "react-icons/tb";
import { FiMessageSquare } from "react-icons/fi";
import CodeEditor from "./components/editor";
import DraggableComponent from "./components/draggable";
import GraphPanel from "./components/GraphPanel";
import ListPanel from "./components/ListPanel";
import HeapPanel from "./components/HeapPanel";
import DictPanel from "./components/DictPanel";
import SettingsMenu from "./components/SettingsMenu";
import TimelineSlider from "./components/TimelineSlider";
import AIChatPanel from "./components/AIChatPanel";

import { RunResponse, BackendStructure, TimelineEvent, TimelineState } from "./types/backend";
import type { ContextAttachment } from "./types/ai";

type PanelKind = BackendStructure["type"] | "log" | "output";

interface PanelState {
  id: string;
  title: string;
  datatype: string;
  varname: string;
  kind: PanelKind;
  payload: any;
  operations?: string[];
  size: { width: number; height: number };
}

function toPanelStates(structures: BackendStructure[]): PanelState[] {
  return (structures ?? []).map((s) => {
    const typeLabel = s.type.charAt(0).toUpperCase() + s.type.slice(1);

    let width = 400;
    let height = 300;

    if (s.type === "graph") {
      const nodeCount = s.payload?.nodes?.length || 0;
      width = Math.max(260, Math.min(420, nodeCount * 50 + 160));
      height = Math.max(220, Math.min(340, nodeCount * 40 + 120));
    } else if (s.type === "list") {
      const itemCount = s.payload?.length || 0;
      height = Math.max(160, Math.min(320, itemCount * 24 + 140));
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

    return {
      id: `struct-${s.name}`,
      title: `${typeLabel}: ${s.name}`,
      datatype: typeLabel,
      varname: s.name,
      kind: s.type,
      payload: s.payload,
      operations: s.operations,
      size: { width, height },
    };
  });
}

export default function App() {
  const [code, setCode] = useState<string>(
    `\n# Welcome to Visual Debugger\n# Paste Python code and click Run\n`
  );
  const [panels, setPanels] = useState<PanelState[]>([]);
  const [output, setOutput] = useState<string>("");
  const [isRunning, setIsRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeId, setActiveId] = useState<string | null>(null);
  const [zCounter, setZCounter] = useState(20);
  const [zMap, setZMap] = useState<Record<string, number>>({});

  // Timeline state
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [timelineStates, setTimelineStates] = useState<TimelineState[]>([]);
  const [finalStructures, setFinalStructures] = useState<BackendStructure[]>([]);
  const [showTimeline, setShowTimeline] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightedLine, setHighlightedLine] = useState<number | null>(null);

  // AI Chat state
  const [isAIChatOpen, setIsAIChatOpen] = useState(false);
  const [contextAttachments, setContextAttachments] = useState<ContextAttachment[]>([]);
  const [selectedCode, setSelectedCode] = useState<{ text: string; startLine: number; endLine: number } | null>(null);

  const handleChange = (value: string) => {
    setCode(value ?? "");
  };

  // AI context attachment handlers
  const handleAddContextAttachment = useCallback((attachment: ContextAttachment) => {
    setContextAttachments((prev) => {
      if (prev.some((a) => a.id === attachment.id)) return prev;
      return [...prev, attachment];
    });
    if (!isAIChatOpen) setIsAIChatOpen(true);
  }, [isAIChatOpen]);

  const handleRemoveAttachment = useCallback((id: string) => {
    setContextAttachments((prev) => prev.filter((a) => a.id !== id));
  }, []);

  const handleClearAttachments = useCallback(() => {
    setContextAttachments([]);
  }, []);

  const handleCodeSelection = useCallback((sel: { text: string; startLine: number; endLine: number } | null) => {
    setSelectedCode(sel);
  }, []);

  const handleAddCodeToContext = useCallback(() => {
    if (!selectedCode) return;
    const attachment: ContextAttachment = {
      id: `ctx-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      type: "code_selection",
      label: selectedCode.startLine === selectedCode.endLine
        ? `Line ${selectedCode.startLine}`
        : `Lines ${selectedCode.startLine}-${selectedCode.endLine}`,
      preview: selectedCode.text.length > 100 ? selectedCode.text.slice(0, 97) + "..." : selectedCode.text,
      fullData: { text: selectedCode.text, startLine: selectedCode.startLine, endLine: selectedCode.endLine },
      timestamp: Date.now(),
    };
    handleAddContextAttachment(attachment);
    setSelectedCode(null);
  }, [selectedCode, handleAddContextAttachment]);

  const handleAddOutputToContext = useCallback(() => {
    const selection = window.getSelection();
    if (!selection || selection.isCollapsed) return;
    const text = selection.toString().trim();
    if (!text) return;
    const attachment: ContextAttachment = {
      id: `ctx-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      type: "terminal_output",
      label: "Terminal Output",
      preview: text.length > 100 ? text.slice(0, 97) + "..." : text,
      fullData: { text },
      timestamp: Date.now(),
    };
    handleAddContextAttachment(attachment);
  }, [handleAddContextAttachment]);

  // Handle timeline step changes
  const handleStepChange = useCallback(
    (step: number) => {
      const maxStep = timelineStates.length > 0 ? timelineStates[timelineStates.length - 1].step : 0;
      const minStep = timelineStates.length > 0 ? timelineStates[0].step : 0;
      const clampedStep = Math.max(minStep, Math.min(maxStep, step));
      setCurrentStep(clampedStep);

      const state = timelineStates.find((s) => s.step === clampedStep);
      if (!state) return;

      setHighlightedLine(state.line ?? null);
      setPanels(toPanelStates(state.structures ?? []));
    },
    [timelineStates]
  );

  // Toggle timeline visualization
  const handleToggleTimeline = useCallback(() => {
    if (timelineStates.length === 0) {
      setError("No timeline data available. Run code first.");
      return;
    }
    
    if (showTimeline) {
      // Close timeline and restore final structures
      setShowTimeline(false);
      setHighlightedLine(null);

      setPanels(toPanelStates(finalStructures));
    } else {
      // Open timeline at the first step
      setShowTimeline(true);
      const firstStep = timelineStates.length > 0 ? timelineStates[0].step : 0;
      setCurrentStep(firstStep);
      handleStepChange(firstStep);
    }
  }, [showTimeline, timelineStates, finalStructures, handleStepChange]);

  const renderPanelContent = (panel: PanelState) => {
    switch (panel.kind) {
      case "graph":
        return (
          <GraphPanel
            data={panel.payload}
            width={panel.size.width - 24}
            height={panel.size.height - 100}
          />
        );
      case "list": {
        return <ListPanel values={panel.payload || []} />;
      }
      case "heap": {
        return <HeapPanel values={panel.payload || []} operations={panel.operations} />;
      }
      case "dict": {
        return <DictPanel entries={panel.payload || {}} />;
      }
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
    setShowTimeline(false);
    setHighlightedLine(null);
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
      if (data.error) setError(data.error);
      if (data.error_line) setHighlightedLine(data.error_line);

      // Store timeline data
      if (data.timeline && Array.isArray(data.timeline)) {
        setTimeline(data.timeline);
      } else {
        setTimeline([]);
      }

      if (data.timeline_states && Array.isArray(data.timeline_states)) {
        setTimelineStates(data.timeline_states);
      } else {
        setTimelineStates([]);
      }

      const nextPanels: PanelState[] = [];

      // console.log("Structures from backend:", data.structures);
      if (Array.isArray(data.structures)) {
        // Store final structures for timeline replay
        setFinalStructures(data.structures);
        
        data.structures.forEach((s, idx) => {
          const typeLabel = s.type.charAt(0).toUpperCase() + s.type.slice(1);
          
          
          let width = 400;
          let height = 300;
          
          // Calculate dynamic size based on structure type and content
          if (s.type === "graph") {
            const nodeCount = s.payload?.nodes?.length || 0;
            width = 200
            height = 300
          } else if (s.type === "list") {
            const itemCount = s.payload?.length || 0;
            height = Math.max(160, Math.min(320, itemCount * 24 + 140));
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
            id: `struct-${s.name}`,
            title: `${typeLabel}: ${s.name}`,
            datatype: typeLabel,
            varname: s.name,
            kind: s.type,
            payload: s.payload,
            operations: s.operations,
            size: { width, height },
          });
        });
      } else {
        setFinalStructures([]);
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

  const draggablePanels = panels;

  const focusPanel = (id: string) => {
    setActiveId(id);
    setZCounter((prev) => {
      const next = prev + 1;
      setZMap((m) => ({ ...m, [id]: next }));
      return next;
    });
  };

  const closePanel = (id: string) => {
    setPanels((prev) => prev.filter((p) => p.id !== id));
    if (activeId === id) {
      setActiveId(panels.find((p) => p.id !== id)?.id ?? null);
    }
  };

  return (
    <div className="relative min-h-screen w-full" style={{ backgroundColor: 'var(--background)', color: 'var(--text)', transition: 'background-color 0.3s ease, color 0.3s ease' }}>
      {/* Main Header */}
      <div className="flex items-center justify-between gap-4 px-6 py-4 border-b" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--subtle-bg)', transition: 'border-color 0.3s ease, background-color 0.3s ease' }}>
        <div className="flex items-center gap-4">
          <img src="/logo.png" alt="Visual Debugger Logo" className="h-12 w-12" />
          <h1 className="text-4xl font-medium" style={{ fontFamily: 'var(--font-instrument-sans)', letterSpacing: 'var(--instrument-sans-letter-spacing)', color: 'var(--text)', transition: 'color 0.3s ease' }}>Visual Debugger</h1>
        </div>
        <SettingsMenu />
      </div>

      {/* Everything else */}
      <div className="mx-auto max-w-6xl px-6 py-16" style={{ transition: "margin-right 0.3s ease", marginRight: isAIChatOpen ? "400px" : undefined }}>
        <div className="flex flex-col gap-3">
          <div className="w-full">
            <div className="flex mb-2">
              <div className="control-group flex w-full border items-stretch justify-end rounded-r-md overflow-visible" style={{letterSpacing: '-0.01em', borderColor: 'var(--border)', transition: 'border-color 0.3s ease', backgroundColor: 'var(--subtle-bg)'}}>
                <button
                  onClick={runCode}
                  disabled={isRunning}
                  className="run-button group"
                  aria-label="Run code"
                >
                  {isRunning ? (
                    <>
                      <div className="animated-dots">
                        <TbDotsDiagonal className="dot-icon" />
                        <TbDotsVertical className="dot-icon" />
                        <TbDotsDiagonal2 className="dot-icon" />
                      </div>
                      <span>Running</span>
                    </>
                  ) : (
                    <>
                      <PiPlayFill className="icon-play" />
                      <span>Run</span>
                    </>
                  )}
                </button>

                <button
                  onClick={handleToggleTimeline}
                  disabled={isRunning || timeline.length === 0}
                  className="action-buttons group"
                  aria-label="Visualize Timeline"
                  // title={timeline.length === 0 ? "Run code first to generate timeline" : "Visualize execution timeline"}
                >
                  <div className="button-tooltip">
                    <span className="tooltip-text">Step through code execution</span>
                    <span className="tooltip-shortcut">Ctrl+T / ⌘+T</span>
                  </div>
                  {showTimeline ? "Exit Timeline" : "Timeline"}
                </button>

                <button
                  onClick={() => setIsAIChatOpen(!isAIChatOpen)}
                  className={`action-buttons group${isAIChatOpen ? " ai-active" : ""}`}
                  aria-label="AI Assistant"
                >
                  <div className="button-tooltip">
                    <span className="tooltip-text">AI debugging assistant</span>
                    <span className="tooltip-shortcut">Ctrl+Shift+A</span>
                  </div>
                  <FiMessageSquare size={14} />
                  AI
                </button>

              </div>
            </div>
            <div className="rounded-xl border overflow-hidden" style={{ position: "relative", zIndex: 10, borderColor: 'var(--border)', transition: 'border-color 0.3s ease' }}>
                <CodeEditor code={code} onChange={handleChange} height="50vh" highlightedLine={highlightedLine} onSelectionChange={handleCodeSelection} />
                {selectedCode && (
                  <button
                    onClick={handleAddCodeToContext}
                    className="add-to-ai-btn"
                    style={{
                      position: "absolute",
                      bottom: "12px",
                      right: "12px",
                      zIndex: 20,
                      display: "flex",
                      alignItems: "center",
                      gap: "6px",
                      padding: "6px 12px",
                      borderRadius: "6px",
                      border: "1px solid var(--accent)",
                      background: "var(--accent)",
                      color: "#fff",
                      fontSize: "12px",
                      fontWeight: 600,
                      cursor: "pointer",
                      boxShadow: "0 2px 8px rgba(0,0,0,0.2)",
                      transition: "opacity 0.15s ease",
                      opacity: 0.95,
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.opacity = "1"; }}
                    onMouseLeave={(e) => { e.currentTarget.style.opacity = "0.95"; }}
                  >
                    <FiMessageSquare size={12} />
                    Add to AI
                  </button>
                )}
            </div>
           
          </div>

          <div className="w-full">
            <div className="card rounded-lg border py-2 px-4 text-sm h-[10vh] overflow-auto" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--subtle-bg)', color: 'var(--foreground)', transition: 'border-color 0.3s ease, background-color 0.3s ease, color 0.3s ease', position: "relative" }}>
              <div className="mb-2 font-semibold text-sm flex items-center justify-between" style={{ color: 'var(--foreground)', opacity: 0.85 }}>
                <span>Output</span>
                <button
                  onClick={handleAddOutputToContext}
                  style={{
                    background: "none",
                    border: "none",
                    color: "var(--accent)",
                    cursor: "pointer",
                    fontSize: "11px",
                    fontWeight: 500,
                    opacity: 0.7,
                    display: "flex",
                    alignItems: "center",
                    gap: "4px",
                    padding: "2px 6px",
                    borderRadius: "4px",
                    transition: "opacity 0.15s ease",
                  }}
                  onMouseEnter={(e) => { e.currentTarget.style.opacity = "1"; }}
                  onMouseLeave={(e) => { e.currentTarget.style.opacity = "0.7"; }}
                  title="Select text and click to add to AI context"
                >
                  <FiMessageSquare size={11} />
                  Add to AI
                </button>
              </div>
              <pre className="font-mono text-sm" style={{ color: 'var(--foreground)' }}>{output || ""}</pre>
              {error && <div className="mt-2 text-sm" style={{ color: '#ff6b6b' }}>Error: {error}</div>}
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
            datatype={panel.datatype}
            varname={panel.varname}
            defaultX={80 + idx * 40}
            defaultY={100 + idx * 30}
            defaultWidth={panel.size.width}
            defaultHeight={panel.size.height}
            zIndex={zMap[panel.id] ?? 10 + idx}
            onFocus={focusPanel}
            onClose={closePanel}
            onAskAI={handleAddContextAttachment}
            panelKind={panel.kind}
            panelPayload={panel.payload}
          >
            {renderPanelContent(panel)}
          </DraggableComponent>
        ))}

        {/* Timeline Slider */}
        {showTimeline && (
          <TimelineSlider
            timeline={timeline}
            currentStep={currentStep}
            onStepChange={handleStepChange}
            onClose={handleToggleTimeline}
          />
        )}

      {/* AI Chat Panel */}
      <AIChatPanel
        isOpen={isAIChatOpen}
        onClose={() => setIsAIChatOpen(false)}
        contextAttachments={contextAttachments}
        onRemoveAttachment={handleRemoveAttachment}
        onClearAttachments={handleClearAttachments}
        code={code}
        output={output}
        panels={panels}
      />
    </div>
  );
}
