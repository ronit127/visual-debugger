"use client";

import React from "react";
import { GoX, GoCode, GoTerminal, GoGraph } from "react-icons/go";
import type { ContextAttachment } from "../types/ai";

interface ContextChipProps {
  attachment: ContextAttachment;
  onRemove?: (id: string) => void;
  compact?: boolean;
}

const typeIcons: Record<ContextAttachment["type"], React.ReactNode> = {
  code_selection: <GoCode size={12} />,
  terminal_output: <GoTerminal size={12} />,
  visualization: <GoGraph size={12} />,
};

const ContextChip: React.FC<ContextChipProps> = ({ attachment, onRemove, compact = false }) => {
  return (
    <div
      className={compact ? "context-chip context-chip-compact" : "context-chip"}
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: "6px",
        padding: compact ? "2px 8px" : "4px 10px",
        borderRadius: "6px",
        fontSize: compact ? "11px" : "12px",
        fontWeight: 500,
        background: "var(--segment-bg)",
        color: "var(--panel-text)",
        border: "1px solid var(--border)",
        maxWidth: "200px",
        transition: "background-color 0.2s ease, border-color 0.2s ease, color 0.2s ease",
      }}
    >
      <span style={{ display: "flex", alignItems: "center", opacity: 0.7 }}>
        {typeIcons[attachment.type]}
      </span>
      <span
        style={{
          overflow: "hidden",
          textOverflow: "ellipsis",
          whiteSpace: "nowrap",
        }}
      >
        {attachment.label}
      </span>
      {onRemove && (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onRemove(attachment.id);
          }}
          style={{
            background: "none",
            border: "none",
            color: "var(--panel-text)",
            opacity: 0.5,
            cursor: "pointer",
            padding: 0,
            display: "flex",
            alignItems: "center",
          }}
          aria-label={`Remove ${attachment.label}`}
        >
          <GoX size={12} />
        </button>
      )}
    </div>
  );
};

export default ContextChip;
