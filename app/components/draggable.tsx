"use client";

import React, { ReactNode, useState } from "react";
import { Rnd } from "react-rnd";
import SVGComponent from "./svg";
import Graph, { GraphAPI } from "./Graph";

interface DraggableComponentProps {
  id: string;
  zIndex?: number;
  type?: "svg" | "graph";
  title?: string;
  defaultWidth?: number;
  defaultHeight?: number;
  defaultX?: number;
  defaultY?: number;
  children?: ReactNode;
  onFocus?: (id: string) => void;
  onClose?: (id: string) => void;
  isActive?: boolean;
}

const DraggableComponent: React.FC<DraggableComponentProps> = ({
  id,
  zIndex,
  type = "svg",
  title = "Window",
  defaultWidth = 300,
  defaultHeight = 200,
  defaultX = 0,
  defaultY = 0,
  children,
  onFocus,
  onClose,
  isActive = false,
}) => {
  const [graphAPI, setGraphAPI] = useState<GraphAPI | null>(null);
  const [position, setPosition] = useState({ x: defaultX, y: defaultY });
  const [size, setSize] = useState({ width: defaultWidth, height: defaultHeight });

  const renderContent = () => {
    if (children) return <>{children}</>;
    if (type === "graph") {
      return <Graph width={size.width} height={size.height} onGraphReady={(api) => setGraphAPI(api)} />;
    }
    return <SVGComponent />;
  };

  const handleFocus = () => onFocus?.(id);
  const handleClose = (e: React.MouseEvent) => {
    e.stopPropagation();
    onClose?.(id);
  };

  return (
    <Rnd
      position={position}
      size={size}
      onDragStop={(e, d) => setPosition({ x: d.x, y: d.y })}
      onResizeStop={(e, direction, ref, delta, position) => {
        setSize({ width: parseInt(ref.style.width), height: parseInt(ref.style.height) });
        setPosition(position);
      }}
      minHeight={100}
      minWidth={150}
      bounds="window"
      dragHandleClassName="drag-area"
      cancel=".no-drag"
      onMouseDown={handleFocus}
      style={{
        zIndex,
      }}
      className={isActive ? "active-panel" : ""}
    >
      <div
        style={{
          borderRadius: "10px",
          overflow: "hidden",
          width: "100%",
          height: "100%",
          boxShadow: isActive ? "0 10px 30px rgba(0,0,0,0.25)" : "0 4px 16px rgba(0,0,0,0.12)",
          transition: "box-shadow 0.2s ease",
        }}
      >
        <div className={`drag-area glass-nav`}>
          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <div
              className="no-drag close-button"
              onClick={handleClose}
              role="button"
              aria-label={`Close ${title}`}
            />
            <div className="whimsy-dot" aria-hidden="true" />
          </div>

          <div className="panel-title">{title}</div>

          <div className="glass-controls no-drag">
            {/* place for future controls, keep it no-drag so clicks don't start dragging */}
            <div className="whimsy-dot" aria-hidden="true" />
          </div>
        </div>

        <div
          className="no-drag"
          style={{
            position: "relative",
            width: "100%",
            height: "calc(100% - 40px)",
            boxSizing: "border-box",
            padding: type === "graph" ? "10px" : "20px",
            background: "#f0f0f0",
            border: "1px solid #ccc",
            color: "black",
            overflow: "auto",
            cursor: "auto",
          }}
        >
          {renderContent()}
        </div>
      </div>
    </Rnd>
  );
};

export default DraggableComponent;