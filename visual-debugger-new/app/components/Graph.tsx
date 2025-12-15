"use client";

import React, { useEffect, useRef } from "react";
import * as d3 from "d3";

export interface GraphNode extends d3.SimulationNodeDatum {
  id: number;
  label: string;
}

export interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
  source: number | GraphNode;
  target: number | GraphNode;
}

interface GraphProps {
  width?: number;
  height?: number;
  onGraphReady?: (api: GraphAPI) => void;
}

export interface GraphAPI {
  addNode: (label: string, id?: number | null, x?: number | null, y?: number | null) => GraphAPI;
  deleteNode: (nodeId: number) => GraphAPI;
  updateNode: (nodeId: number, properties: Partial<GraphNode>) => GraphAPI;
  getNode: (nodeId: number) => GraphNode | null;
  getNodes: () => GraphNode[];
  addEdge: (sourceId: number, targetId: number, properties?: any) => GraphAPI;
  deleteEdge: (sourceId: number, targetId: number) => GraphAPI;
  getEdge: (sourceId: number, targetId: number) => GraphLink | null;
  getEdges: () => GraphLink[];
  clear: () => GraphAPI;
  setGraph: (newNodes: GraphNode[], newLinks: GraphLink[]) => GraphAPI;
  getNeighbors: (nodeId: number) => number[];
  getDegree: (nodeId: number) => number;
  exportGraph: () => { nodes: GraphNode[]; links: GraphLink[]; nextId: number };
}

const Graph: React.FC<GraphProps> = ({ width = 800, height = 600, onGraphReady }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const nodesRef = useRef<GraphNode[]>([]);
  const linksRef = useRef<GraphLink[]>([]);
  const nextIdRef = useRef(1);
  const simulationRef = useRef<d3.Simulation<GraphNode, GraphLink> | null>(null);

  useEffect(() => {
    if (!svgRef.current) return;

    const svg = d3.select(svgRef.current);
    const R = 20;
    const PAD = 4;
    const jitter = (n = 10) => (Math.random() - 0.5) * 2 * n;

    // Clear existing content
    svg.selectAll("*").remove();

    // Create simulation
    const simulation = d3
      .forceSimulation<GraphNode>(nodesRef.current)
      .velocityDecay(0.35)
      .force("link", d3.forceLink<GraphNode, GraphLink>(linksRef.current).id((d) => d.id).distance(80))
      .force("charge", d3.forceManyBody<GraphNode>().strength(-120))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(0.05))
      .force("y", d3.forceY(height / 2).strength(0.05));

    simulationRef.current = simulation;

    // Container groups
    const linkG = svg.append("g").attr("class", "links");
    const nodeG = svg.append("g").attr("class", "nodes");

    // Drag behavior
    function drag(sim: d3.Simulation<GraphNode, GraphLink>) {
      function started(event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>, d: GraphNode) {
        if (!event.active) sim.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      function dragged(event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>, d: GraphNode) {
        d.fx = event.x;
        d.fy = event.y;
      }
      function ended(event: d3.D3DragEvent<SVGGElement, GraphNode, GraphNode>, d: GraphNode) {
        if (!event.active) sim.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
      return d3.drag<SVGGElement, GraphNode>().on("start", started).on("drag", dragged).on("end", ended);
    }

    // Update function
    function updateGraph() {
      // LINKS
      const link = linkG
        .selectAll<SVGLineElement, GraphLink>("line.link")
        .data(linksRef.current, (d) => `${(d.source as GraphNode).id}-${(d.target as GraphNode).id}`);
      link.exit().remove();
      link
        .enter()
        .append("line")
        .attr("class", "link")
        .attr("stroke", "#999")
        .attr("stroke-width", 2)
        .merge(link);

      // NODES
      const node = nodeG.selectAll<SVGGElement, GraphNode>("g.node-group").data(nodesRef.current, (d) => String(d.id));
      node.exit().remove();

      const nodeEnter = node.enter().append("g").attr("class", "node-group").call(drag(simulation));

      // circle
      nodeEnter
        .append("circle")
        .attr("class", "node-circle")
        .attr("r", R)
        .attr("fill", "#69b3a2")
        .attr("stroke", "#333")
        .attr("stroke-width", 2);

      // label
      nodeEnter
        .append("text")
        .attr("class", "node-label")
        .attr("dy", 5)
        .attr("text-anchor", "middle")
        .attr("fill", "white")
        .attr("font-size", "12px")
        .attr("font-weight", "bold")
        .text((d) => d.label);

      // delete X
      nodeEnter
        .append("text")
        .attr("class", "delete-btn")
        .attr("x", 15)
        .attr("y", -15)
        .attr("text-anchor", "middle")
        .attr("fill", "red")
        .attr("font-size", "16px")
        .attr("font-weight", "bold")
        .attr("cursor", "pointer")
        .text("✕")
        .on("click", (event, d) => {
          api.deleteNode(d.id);
          event.stopPropagation();
        });

      node.merge(nodeEnter);

      // RESTART SIMULATION
      simulation.nodes(nodesRef.current);
      (simulation.force("link") as d3.ForceLink<GraphNode, GraphLink>).links(linksRef.current);
      simulation.alpha(1).restart();

      simulation.on("tick", () => {
        linkG
          .selectAll<SVGLineElement, GraphLink>("line.link")
          .attr("x1", (d) => (d.source as GraphNode).x ?? 0)
          .attr("y1", (d) => (d.source as GraphNode).y ?? 0)
          .attr("x2", (d) => (d.target as GraphNode).x ?? 0)
          .attr("y2", (d) => (d.target as GraphNode).y ?? 0);

        nodeG
          .selectAll<SVGGElement, GraphNode>("g.node-group")
          .each(function (d) {
            const minX = R + PAD,
              maxX = width - R - PAD;
            const minY = R + PAD,
              maxY = height - R - PAD;
            if (d.x !== undefined && d.x < minX) {
              d.x = minX;
              d.vx = 0;
            }
            if (d.x !== undefined && d.x > maxX) {
              d.x = maxX;
              d.vx = 0;
            }
            if (d.y !== undefined && d.y < minY) {
              d.y = minY;
              d.vy = 0;
            }
            if (d.y !== undefined && d.y > maxY) {
              d.y = maxY;
              d.vy = 0;
            }
          })
          .attr("transform", (d) => `translate(${d.x ?? 0},${d.y ?? 0})`);
      });
    }

    // API
    const api: GraphAPI = {
      setGraph: (newNodes: GraphNode[], newLinks: GraphLink[]) => {
        nodesRef.current = newNodes.map((n) => ({ ...n }));
        linksRef.current = newLinks.map((l) => ({ ...l }));
        if (nodesRef.current.length > 0) {
          nextIdRef.current = Math.max(...nodesRef.current.map((n) => n.id)) + 1;
        }
        updateGraph();
        return api;
      },

      addNode: (label: string, id: number | null = null, x: number | null = null, y: number | null = null) => {
        const nodeId = id !== null ? id : nextIdRef.current;
        const nodeLabel = label || String(nodeId);

        if (nodesRef.current.find((n) => n.id === nodeId)) {
          console.warn(`Node with id ${nodeId} already exists`);
          return api;
        }

        const newNode: GraphNode = {
          id: nodeId,
          label: nodeLabel,
          x: x !== null ? x : width / 2 + jitter(10),
          y: y !== null ? y : height / 2 + jitter(10),
        };

        if (x !== null && y !== null) {
          newNode.fx = x;
          newNode.fy = y;
        }

        nodesRef.current.push(newNode);

        if (id === null) {
          nextIdRef.current++;
        } else if (nodeId >= nextIdRef.current) {
          nextIdRef.current = nodeId + 1;
        }

        updateGraph();
        return api;
      },

      deleteNode: (nodeId: number) => {
        const initialLength = nodesRef.current.length;
        nodesRef.current = nodesRef.current.filter((n) => n.id !== nodeId);
        linksRef.current = linksRef.current.filter(
          (l) => (l.source as GraphNode).id !== nodeId && (l.target as GraphNode).id !== nodeId
        );

        if (nodesRef.current.length < initialLength) {
          updateGraph();
        }
        return api;
      },

      updateNode: (nodeId: number, properties: Partial<GraphNode>) => {
        const node = nodesRef.current.find((n) => n.id === nodeId);
        if (node) {
          Object.assign(node, properties);
          updateGraph();
        }
        return api;
      },

      getNode: (nodeId: number) => {
        return nodesRef.current.find((n) => n.id === nodeId) || null;
      },

      getNodes: () => {
        return [...nodesRef.current];
      },

      addEdge: (sourceId: number, targetId: number, properties: any = {}) => {
        const sourceNode = nodesRef.current.find((n) => n.id === sourceId);
        const targetNode = nodesRef.current.find((n) => n.id === targetId);

        if (!sourceNode || !targetNode) {
          console.warn(`Cannot add edge: source (${sourceId}) or target (${targetId}) node not found`);
          return api;
        }

        if (sourceId === targetId) {
          console.warn("Self-loops are not supported");
          return api;
        }

        const existingEdge = linksRef.current.find(
          (l) =>
            ((l.source as GraphNode).id === sourceId && (l.target as GraphNode).id === targetId) ||
            ((l.source as GraphNode).id === targetId && (l.target as GraphNode).id === sourceId)
        );

        if (existingEdge) {
          console.warn(`Edge between ${sourceId} and ${targetId} already exists`);
          return api;
        }

        const newLink: GraphLink = { source: sourceId, target: targetId, ...properties };
        linksRef.current.push(newLink);
        updateGraph();
        return api;
      },

      deleteEdge: (sourceId: number, targetId: number) => {
        const initialLength = linksRef.current.length;
        linksRef.current = linksRef.current.filter(
          (l) =>
            !(
              ((l.source as GraphNode).id === sourceId && (l.target as GraphNode).id === targetId) ||
              ((l.source as GraphNode).id === targetId && (l.target as GraphNode).id === sourceId)
            )
        );

        if (linksRef.current.length < initialLength) {
          updateGraph();
        }
        return api;
      },

      getEdge: (sourceId: number, targetId: number) => {
        return (
          linksRef.current.find(
            (l) =>
              ((l.source as GraphNode).id === sourceId && (l.target as GraphNode).id === targetId) ||
              ((l.source as GraphNode).id === targetId && (l.target as GraphNode).id === sourceId)
          ) || null
        );
      },

      getEdges: () => {
        return [...linksRef.current];
      },

      clear: () => {
        nodesRef.current = [];
        linksRef.current = [];
        nextIdRef.current = 1;
        updateGraph();
        return api;
      },

      getNeighbors: (nodeId: number) => {
        const neighbors: number[] = [];
        linksRef.current.forEach((link) => {
          if ((link.source as GraphNode).id === nodeId) {
            neighbors.push((link.target as GraphNode).id);
          } else if ((link.target as GraphNode).id === nodeId) {
            neighbors.push((link.source as GraphNode).id);
          }
        });
        return [...new Set(neighbors)];
      },

      getDegree: (nodeId: number) => {
        return api.getNeighbors(nodeId).length;
      },

      exportGraph: () => {
        return {
          nodes: api.getNodes(),
          links: api.getEdges(),
          nextId: nextIdRef.current,
        };
      },
    };

    // Notify parent component
    if (onGraphReady) {
      onGraphReady(api);
    }

    // Initial render
    updateGraph();

    return () => {
      simulation.stop();
    };
  }, [width, height, onGraphReady]);

  return <svg ref={svgRef} width={width} height={height} className="bg-white border border-gray-300 rounded-lg" />;
};

export default Graph;
