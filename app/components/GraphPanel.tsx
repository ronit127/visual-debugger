"use client";

import React, { useEffect, useState } from "react";
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

  useEffect(() => {
    if (!api) return;
    api.clear();
    api.setGraph(data.nodes || [], data.links || []);
  }, [api, data]);

  return <Graph width={width} height={height} onGraphReady={setApi} />;
};

export default GraphPanel;
