"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import Graph, { GraphAPI, GraphLink, GraphNode } from "./Graph";

export interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

interface GraphPanelProps {
  data: GraphData;
  width?: number;
  height?: number;
}

const GraphPanel: React.FC<GraphPanelProps> = ({ data, width = 500, height = 400 }) => {
  const [api, setApi] = useState<GraphAPI | null>(null);
  const prevHashRef = useRef<string>("");
  const containerRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState({ width, height });

  const hashGraph = (graph: GraphData) => {
    const nodes = (graph.nodes || [])
      .map((n) => `${n.id}:${n.label}`)
      .sort()
      .join("|");
    const links = (graph.links || [])
      .map((l) => {
        const s = typeof l.source === "object" ? l.source.id : l.source;
        const t = typeof l.target === "object" ? l.target.id : l.target;
        return s < t ? `${s}-${t}` : `${t}-${s}`;
      })
      .sort()
      .join("|");
    return `${nodes}::${links}`;
  };

  useEffect(() => {
    if (!containerRef.current) return;

    const node = containerRef.current;
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const { width: w, height: h } = entry.contentRect;
        if (w > 0 && h > 0) {
          setSize({ width: Math.floor(w), height: Math.floor(h) });
        }
      }
    });

    observer.observe(node);
    return () => observer.disconnect();
  }, []);

  useEffect(() => {
    if (!api) return;
    const nextHash = hashGraph(data);
    if (nextHash === prevHashRef.current) return;
    prevHashRef.current = nextHash;
    api.clear();
    api.setGraph(data.nodes || [], data.links || []);
  }, [api, data]);

  const graphSize = useMemo(() => {
    return {
      width: size.width || width,
      height: size.height || height,
    };
  }, [size, width, height]);

  return (
    <div ref={containerRef} className="h-full w-full">
      <Graph width={graphSize.width} height={graphSize.height} onGraphReady={setApi} />
    </div>
  );
};

export default GraphPanel;
