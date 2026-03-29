"use client";

import React, { useEffect, useRef, useCallback } from "react";
import * as d3 from "d3";

interface ListPanelProps {
  values: any[];
  highlightIndex?: number | null;
}

interface ListNode {
  id: number;
  value: any;
  x: number;
  y: number;
}

const ListPanel: React.FC<ListPanelProps> = ({ values, highlightIndex = null }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const isDraggingRef = useRef(false);
  const offsetRef = useRef({ x: 0, y: 0 });
  const prevValuesRef = useRef<any[]>([]);

  const safeString = (value: any) => {
    try {
      return JSON.stringify(value);
    } catch {
      return String(value);
    }
  };

  const update = useCallback(() => {
    if (!svgRef.current || !containerRef.current) return;

    const svg = d3.select(svgRef.current);
    const containerWidth = containerRef.current.clientWidth;
    const containerHeight = containerRef.current.clientHeight;

    // Theme detection
    const isDark = document.documentElement.classList.contains('dark');
    const computed = getComputedStyle(document.documentElement);
    
    // Monochrome palette with single accent
    const colors = {
      bg: isDark ? '#1e1e1e' : '#fafafa',
      border: isDark ? '#404040' : '#d4d4d4',
      borderActive: isDark ? '#60a5fa' : '#3b82f6',
      text: isDark ? '#e5e5e5' : '#171717',
      textMuted: isDark ? '#a3a3a3' : '#737373',
      connector: isDark ? '#525252' : '#a3a3a3',
      accent: isDark ? '#60a5fa' : '#3b82f6',
    };

    // Layout constants
    const NODE_SIZE = 56;
    const GAP = 6;
    const PADDING = 20;
    const INDEX_OFFSET = 16;
    const DURATION = 360;
    const easeMove = d3.easeCubicInOut;
    const easeInOut = d3.easeCubicOut;

    const prevSerialized = prevValuesRef.current.map(safeString);
    const nextSerialized = values.map(safeString);
    let changeIndex = nextSerialized.findIndex((v, i) => prevSerialized[i] !== v);
    if (changeIndex === -1 && prevSerialized.length !== nextSerialized.length) {
      changeIndex = Math.min(prevSerialized.length, nextSerialized.length);
    }
    const insertionIndex = nextSerialized.length > prevSerialized.length ? changeIndex : null;
    const removalIndex = nextSerialized.length < prevSerialized.length ? changeIndex : null;

    // Calculate layout
    const totalItemWidth = NODE_SIZE + GAP;
    const totalWidth = values.length * totalItemWidth - GAP + PADDING * 2;
    const totalHeight = NODE_SIZE + INDEX_OFFSET + PADDING * 2;

    // Calculate positions
    const newNodes: ListNode[] = values.map((value, idx) => {
      const listWidth = values.length * totalItemWidth - GAP;
      const startX = Math.max(PADDING, (containerWidth - listWidth) / 2);
      return {
        id: idx,
        value,
        x: startX + NODE_SIZE / 2 + idx * totalItemWidth,
        y: PADDING + NODE_SIZE / 2,
      };
    });

    // Set SVG size
    const svgHeight = Math.max(containerHeight, totalHeight);
    const svgWidth = Math.max(containerWidth, totalWidth);
    
    svg.attr("width", svgWidth).attr("height", svgHeight);

    // Initialize groups if needed
    let mainG = svg.select<SVGGElement>("g.main-group");
    if (mainG.empty()) {
      mainG = svg.append("g").attr("class", "main-group");
      mainG.append("g").attr("class", "nodes");
    }
    const nodesG = mainG.select<SVGGElement>("g.nodes");



    // Drag behavior for entire list
    const dragBehavior = d3.drag<SVGGElement, unknown>()
      .on("start", () => {
        isDraggingRef.current = true;
        const transform = mainG.attr("transform");
        const match = transform?.match(/translate\(([^,]+),([^)]+)\)/);
        offsetRef.current = {
          x: match ? parseFloat(match[1]) : 0,
          y: match ? parseFloat(match[2]) : 0,
        };
      })
      .on("drag", (event) => {
        const newX = offsetRef.current.x + event.x - event.subject.x;
        const newY = offsetRef.current.y + event.y - event.subject.y;
        mainG.attr("transform", `translate(${newX},${newY})`);
      })
      .on("end", () => {
        isDraggingRef.current = false;
      });

    mainG.call(dragBehavior as any).style("cursor", "grab");

    // Handle empty state
    if (!values || values.length === 0) {
      nodesG.selectAll("*").remove();
      
      const emptyG = nodesG.selectAll<SVGGElement, null>("g.empty")
        .data([null]);
      
      const emptyEnter = emptyG.enter().append("g").attr("class", "empty");
      
      emptyEnter.append("rect")
        .attr("width", 120)
        .attr("height", NODE_SIZE)
        .attr("rx", 4)
        .attr("fill", "none")
        .attr("stroke", colors.border)
        .attr("stroke-width", 1)
        .attr("stroke-dasharray", "4,4");

      emptyEnter.append("text")
        .attr("x", 60)
        .attr("y", NODE_SIZE / 2 + 4)
        .attr("text-anchor", "middle")
        .attr("fill", colors.textMuted)
        .attr("font-size", "12px")
        .attr("font-family", "'JetBrains Mono', 'SF Mono', 'Fira Code', monospace")
        .text("[ ]");

      emptyG.merge(emptyEnter)
        .attr("transform", `translate(${containerWidth / 2 - 60}, ${containerHeight / 2 - NODE_SIZE / 2})`);

      return;
    }

    // Remove empty state if exists
    nodesG.selectAll("g.empty").remove();

    // === NODES (enter/update/exit) ===
    const nodes = nodesG.selectAll<SVGGElement, ListNode>("g.list-node")
      .data(newNodes, d => String(d.id));

    // Exit
    nodes.exit()
      .transition()
      .duration(DURATION)
      .ease(easeInOut)
      .style("opacity", 0)
      .attr("transform", d => {
        const idx = (d as ListNode).id;
        const dx = removalIndex === 0 ? -22 : removalIndex === prevSerialized.length - 1 ? 22 : 0;
        const dy = removalIndex != null && removalIndex > 0 && removalIndex < prevSerialized.length - 1 ? 10 : 0;
        return `translate(${(d as ListNode).x + dx}, ${(d as ListNode).y + dy}) scale(0.96)`;
      })
      .remove();

    // Enter
    const nodeEnter = nodes.enter()
      .append("g")
      .attr("class", "list-node")
      .attr("transform", d => {
        const idx = d.id;
        const dx = insertionIndex === 0 ? -22 : insertionIndex === values.length - 1 ? 22 : 0;
        const dy = insertionIndex != null && insertionIndex > 0 && insertionIndex < values.length - 1 ? 10 : 0;
        return `translate(${d.x + dx}, ${d.y + dy})`;
      })
      .style("opacity", 0);

    nodeEnter.append("rect")
      .attr("class", "node-rect")
      .attr("x", -NODE_SIZE / 2)
      .attr("y", -NODE_SIZE / 2)
      .attr("width", NODE_SIZE)
      .attr("height", NODE_SIZE)
      .attr("rx", 4)
      .attr("fill", "transparent")
      .attr("stroke", colors.border)
      .attr("stroke-width", 1);

    nodeEnter.append("text")
      .attr("class", "node-index")
      .attr("y", NODE_SIZE / 2 + INDEX_OFFSET)
      .attr("text-anchor", "middle")
      .attr("fill", colors.textMuted)
      .attr("font-size", "10px")
      .attr("font-family", "'JetBrains Mono', 'SF Mono', 'Fira Code', monospace");

    nodeEnter.append("text")
      .attr("class", "node-value")
      .attr("y", 5)
      .attr("text-anchor", "middle")
      .attr("fill", colors.text)
      .attr("font-size", "13px")
      .attr("font-weight", "500")
      .attr("font-family", "'JetBrains Mono', 'SF Mono', 'Fira Code', monospace");

    // Active indicator (caret)
    nodeEnter.append("polygon")
      .attr("class", "node-caret")
      .attr("fill", colors.accent)
      .style("opacity", 0);

    // Merge and update
    const allNodes = nodeEnter.merge(nodes);

    const baseDelay = (id: number) => {
      if (changeIndex == null || changeIndex < 0) return 0;
      return Math.min(120, Math.abs(id - changeIndex) * 12);
    };

    allNodes
      .transition()
      .duration(DURATION)
      .ease(easeMove)
      .delay(d => baseDelay(d.id))
      .style("opacity", 1)
      .attr("transform", d => `translate(${d.x}, ${d.y})`);

    // Update node content
    allNodes.each(function(d) {
      const g = d3.select(this);
      const isActive = highlightIndex === d.id;
      const isModified = changeIndex != null && (insertionIndex != null || removalIndex != null);
      const isAffected = isModified && (d.id === changeIndex || (insertionIndex != null && d.id > changeIndex) || (removalIndex != null && d.id >= changeIndex));
      
      // Border style for active state and animation
      const strokeColor = isActive ? colors.accent : (isAffected ? colors.accent : colors.border);
      const strokeWidth = isActive ? 2 : (isAffected ? 2 : 1);
      
      g.select(".node-rect")
        .transition().duration(DURATION).ease(easeInOut)
        .attr("stroke", strokeColor)
        .attr("stroke-width", strokeWidth);

      // Fade out accent border for affected elements after animation
      if (isAffected && !isActive) {
        g.select(".node-rect")
          .transition()
          .delay(DURATION + 200)
          .duration(500)
          .ease(d3.easeQuadOut)
          .attr("stroke", colors.border)
          .attr("stroke-width", 1);
      }

      // Index
      g.select(".node-index").text(d.id);

      // Value (truncate if needed)
      const valueStr = typeof d.value === 'string' ? `"${d.value}"` : JSON.stringify(d.value);
      const truncated = valueStr.length > 10 ? valueStr.slice(0, 9) + "…" : valueStr;
      g.select(".node-value")
        .text(truncated)
        .append("title")
        .text(valueStr);

      // Caret indicator
      g.select(".node-caret")
        .attr("points", `${0},${-NODE_SIZE / 2 - 8} ${-5},${-NODE_SIZE / 2 - 14} ${5},${-NODE_SIZE / 2 - 14}`)
        .transition().duration(DURATION).ease(easeInOut)
        .style("opacity", isActive ? 1 : 0);
    });

    prevValuesRef.current = values;

  }, [values, highlightIndex]);

  // Initial render and updates
  useEffect(() => {
    update();
  }, [update]);

  // Handle resize
  useEffect(() => {
    const handleResize = () => update();
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, [update]);

  return (
    <div ref={containerRef} className="h-full w-full overflow-auto list-panel-scroll">
      <svg ref={svgRef} style={{ minWidth: '100%', minHeight: '100%' }} />
    </div>
  );
};

export default ListPanel;
