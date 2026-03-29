"use client";

import React, { ReactNode, useState } from "react";
import { Rnd } from "react-rnd";
import SVGComponent from "./svg";
import Graph from "./Graph";
import { GoX } from "react-icons/go";
import AskButton from "./AskButton";
import type { ContextAttachment } from "../types/ai";

interface DraggableComponentProps {
  id: string;
  zIndex?: number;
  type?: "svg" | "graph";
  title?: string;
  datatype?: string;
  varname?: string;
  defaultWidth?: number;
  defaultHeight?: number;
  defaultX?: number;
  defaultY?: number;
  children?: ReactNode;
  onFocus?: (id: string) => void;
  onClose?: (id: string) => void;
  onAskAI?: (attachment: ContextAttachment) => void;
  panelKind?: string;
  panelPayload?: unknown;
}

const DraggableComponent: React.FC<DraggableComponentProps> = ({
  id,
  zIndex,
  type = "svg",
  title = "Window",
  datatype,
  varname,
  defaultWidth = 300,
  defaultHeight = 200,
  defaultX = 0,
  defaultY = 0,
  children,
  onFocus,
  onClose,
  onAskAI,
  panelKind,
  panelPayload,

}) => {
  const [position, setPosition] = useState({ x: defaultX, y: defaultY });
  const [size, setSize] = useState({ width: defaultWidth, height: defaultHeight });
  const [isDragging, setIsDragging] = useState(false);

  const handleClose = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    onClose?.(id);
  };

  return (
    <Rnd
      position={position}
      size={size}
      onDragStart={() => {
        setIsDragging(true);
        onFocus?.(id);
      }}
      onDragStop={(e, d) => {
        setPosition({ x: d.x, y: d.y });
        setIsDragging(false);
      }}
      onResizeStop={(e, direction, ref) => {
        setSize({ width: parseInt(ref.style.width), height: parseInt(ref.style.height) });
        setPosition({ x: parseInt(ref.style.left) || position.x, y: parseInt(ref.style.top) || position.y });
      }}
      minHeight={100}
      minWidth={150}
      bounds="window"
      dragHandleClassName="drag-area"
      cancel=".no-drag"
      onMouseDown={(e) => {
        const t = e.target as HTMLElement | null;
        if (t?.closest?.('.simple-close-btn')) return;
        onFocus?.(id);
      }}
      style={{ zIndex, background: "transparent" }}
      className={`simple-panel-rnd shadow-sm ${isDragging ? "is-dragging" : ""}`}
    >
      <div className="simple-panel">
        {/* header */}
        <div className="simple-panel-header drag-area">
          {datatype && varname ? (
            <div className="simple-panel-title-container">
              <span className="simple-panel-datatype">{datatype}</span>
              <span className="simple-panel-separator">:</span>
              <span className="simple-panel-varname">{varname}</span>
            </div>
          ) : (
          <span className="simple-panel-title">{title}</span>
          )}
          <div style={{ display: "flex", alignItems: "center", gap: "2px" }}>
            {onAskAI && panelKind && varname && (
              <AskButton
                panelId={id}
                panelKind={panelKind}
                panelTitle={title}
                panelPayload={panelPayload}
                varname={varname}
                onAsk={onAskAI}
              />
            )}
            <button
              className="simple-close-btn no-drag cursor-pointer"
              onMouseDown={handleClose}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  e.stopPropagation();
                  onClose?.(id);
                }
              }}
              aria-label={`Close ${title}`}
            >
              <GoX size={15} />
            </button>
          </div>
        </div>

        {/* content */}
        <div className="simple-panel-content no-drag">
          {children ?? (type === "graph" ? <Graph width={size.width} height={size.height} /> : <SVGComponent />)}
        </div>
      </div>
    </Rnd>
  );
};

export default DraggableComponent;
