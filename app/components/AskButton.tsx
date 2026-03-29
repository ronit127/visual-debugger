"use client";

import React from "react";
import { GoCommentDiscussion } from "react-icons/go";
import type { ContextAttachment } from "../types/ai";

interface AskButtonProps {
  panelId: string;
  panelKind: string;
  panelTitle: string;
  panelPayload: unknown;
  varname: string;
  onAsk: (attachment: ContextAttachment) => void;
}

function buildPreview(kind: string, payload: unknown): string {
  if (kind === "graph") {
    const p = payload as { nodes?: unknown[]; links?: unknown[] };
    return `Graph with ${p?.nodes?.length || 0} nodes, ${p?.links?.length || 0} edges`;
  }
  if (kind === "list") {
    const arr = payload as unknown[];
    if (!arr || arr.length === 0) return "[]";
    if (arr.length <= 6) return `[${arr.map((v) => JSON.stringify(v)).join(", ")}]`;
    return `[${arr.slice(0, 5).map((v) => JSON.stringify(v)).join(", ")}, ... +${arr.length - 5}]`;
  }
  if (kind === "heap") {
    const arr = payload as unknown[];
    if (!arr || arr.length === 0) return "Heap: []";
    return `Heap(${arr.length}): [${arr.slice(0, 5).map((v) => JSON.stringify(v)).join(", ")}${arr.length > 5 ? ", ..." : ""}]`;
  }
  if (kind === "dict") {
    const obj = payload as Record<string, unknown>;
    const keys = Object.keys(obj || {});
    if (keys.length === 0) return "{}";
    return `{${keys.slice(0, 4).join(", ")}${keys.length > 4 ? `, ... +${keys.length - 4}` : ""}}`;
  }
  return JSON.stringify(payload).slice(0, 80);
}

const AskButton: React.FC<AskButtonProps> = ({ panelId, panelKind, panelTitle, panelPayload, varname, onAsk }) => {
  const handleClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    const kindLabel = panelKind.charAt(0).toUpperCase() + panelKind.slice(1);
    const attachment: ContextAttachment = {
      id: `ctx-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      type: "visualization",
      label: `${kindLabel}: ${varname}`,
      preview: buildPreview(panelKind, panelPayload),
      fullData: { type: panelKind, varname, payload: panelPayload },
      panelKind,
      timestamp: Date.now(),
    };
    onAsk(attachment);
  };

  return (
    <button
      className="simple-close-btn no-drag cursor-pointer"
      onClick={handleClick}
      aria-label={`Ask AI about ${panelTitle}`}
      title="Ask AI"
      style={{ opacity: 0.5 }}
      onMouseEnter={(e) => { e.currentTarget.style.opacity = "0.9"; e.currentTarget.style.color = "var(--accent)"; }}
      onMouseLeave={(e) => { e.currentTarget.style.opacity = "0.5"; e.currentTarget.style.color = "var(--panel-text)"; }}
    >
      <GoCommentDiscussion size={14} />
    </button>
  );
};

export default AskButton;
