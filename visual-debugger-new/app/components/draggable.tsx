import React, { useState } from "react";
import { Rnd } from "react-rnd";
import SVGComponent from "./svg";

interface DraggableComponentProps {
  zIndex?: number;
}

const DraggableComponent: React.FC<DraggableComponentProps> = ({ zIndex }) => {
  const [visible, setVisible] = useState(true);
  const [isHovered, setIsHovered] = useState(false);

  if (!visible) return null;

  return (
    <Rnd
      default={{
        x: 0,
        y: 0,
        width: 300,
        height: 200,
      }}
      minHeight="100"
      minWidth="150"
      bounds="window"
      dragHandleClassName="window-title"
      style={{
        borderRadius: "10px",
        overflow: "hidden",
        position: "relative",
        zIndex,
      }}
    >
      <div
        className="window-title"
        style={{
          display: "flex",
          alignItems: "center",
          height: "32px",
          padding: "0 6px",
          backgroundColor: "#3c3c3cff",
        }}
      >
        <div style={{ display: "flex", gap: "8px" }}>
          {/* close window */}
          <div
            id="close"
            style={{
              width: 12,
              height: 12,
              background: "#ff5f56", // red
              borderRadius: "50%",
              cursor: "pointer",
              color: "grey",
              fontWeight: "bold",
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onClick={() => setVisible(false)}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            {isHovered ? "x" : ""}
          </div>
        </div>
      </div>
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
          padding: "20px",
          background: "#f0f0f0",
          border: "1px solid #ccc",
          color: "black",
        }}
      >
        {/* I&apos;m a draggable, closeable, resizeable window! */}
        <SVGComponent />
      </div>
    </Rnd>
  );
};

export default DraggableComponent;
