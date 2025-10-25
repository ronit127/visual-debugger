document.addEventListener('DOMContentLoaded', function() {
  // Graph data
  let nodes = [];
  let links = [];
  let nextId = 1;
  
  // SVG & simulation setup
  const svg = d3.select("#graphSVG");
  const width = +svg.attr("width"), height = +svg.attr("height");

  const R = 20;                 // node radius (keep in sync with your circle r)
  const PAD = 4;                // little padding from edges
  const jitter = (n=10) => (Math.random() - 0.5) * 2 * n; // CHANGED: small helper for spawn jitter

  const simulation = d3.forceSimulation(nodes)
    .velocityDecay(0.35)        // add damping so things slow down faster
    .force("link", d3.forceLink(links).id(d => d.id).distance(80)) // shorter springs
    .force("charge", d3.forceManyBody().strength(-120))            // less repulsion
    .force("center", d3.forceCenter(width/2, height/2))
    .force("x", d3.forceX(width / 2).strength(0.05))               // gentle pull to middle
    .force("y", d3.forceY(height / 2).strength(0.05));             // gentle pull to middle
  
  // Container groups
  const linkG = svg.append("g").attr("class","links");
  const nodeG = svg.append("g").attr("class","nodes");
  
  // DRAGGING BEHAVIOR
  function drag(sim) {
    function started(event,d){
      if (!event.active) sim.alphaTarget(0.3).restart();
      d.fx = d.x; d.fy = d.y;
    }
    function dragged(event,d){
      d.fx = event.x; d.fy = event.y;
    }
    function ended(event,d){
      if (!event.active) sim.alphaTarget(0);
      d.fx = null; d.fy = null;
    }
    return d3.drag()
      .on("start", started)
      .on("drag", dragged)
      .on("end", ended);
  }
  
  // Helper function to update dropdowns
  function updateDropdowns() {
    d3.select('#edgeSrc').selectAll('option:not([disabled])').remove();
    d3.select('#edgeTgt').selectAll('option:not([disabled])').remove();
    nodes.forEach(n => {
      d3.select('#edgeSrc').append('option').attr('value', n.id).text(n.label || n.id);
      d3.select('#edgeTgt').append('option').attr('value', n.id).text(n.label || n.id);
    });
  }
  
  // MAIN UPDATE FUNCTION
  function updateGraph() {
    // LINKS
    const link = linkG.selectAll("line.link")
      .data(links, d => `${d.source.id}-${d.target.id}`);
    link.exit().remove();
    link.enter()
      .append("line")
      .attr("class","link")
      .merge(link);
  
    // NODES
    const node = nodeG.selectAll("g.node-group")
      .data(nodes, d => d.id);
    node.exit().remove();
  
    const nodeEnter = node.enter()
      .append("g")
        .attr("class","node-group")
        .call(drag(simulation));
  
    // circle
    nodeEnter
      .append("circle")
        .attr("class","node-circle")
        .attr("r", R); // CHANGED: use R so clamp matches visual radius
  
    // label
    nodeEnter
      .append("text")
        .attr("class","node-label")
        .attr("dy", 5)
        .attr("text-anchor","middle")
        .text(d => d.label);
  
    // delete X
    nodeEnter
      .append("text")
        .attr("class","delete-btn")
        .attr("x", 15)
        .attr("y", -15)
        .attr("text-anchor","middle")
        .text("X")
        .on("click", (event,d) => {
          window.visualGraph.deleteNode(d.id);
          event.stopPropagation();
        });
  
    node.merge(nodeEnter);
  
    // RESTART SIMULATION
    simulation.nodes(nodes);
    simulation.force("link").links(links);
    simulation.alpha(1).restart();
  
    simulation.on("tick", () => {
      linkG.selectAll("line.link")
        .attr("x1", d=>d.source.x)
        .attr("y1", d=>d.source.y)
        .attr("x2", d=>d.target.x)
        .attr("y2", d=>d.target.y);
  
      // CHANGED: clamp node positions inside the SVG before rendering
      nodeG.selectAll("g.node-group")
        .each(function(d) {
          const minX = R + PAD, maxX = width - R - PAD;
          const minY = R + PAD, maxY = height - R - PAD;
          if (d.x < minX) { d.x = minX; d.vx = 0; }
          if (d.x > maxX) { d.x = maxX; d.vx = 0; }
          if (d.y < minY) { d.y = minY; d.vy = 0; }
          if (d.y > maxY) { d.y = maxY; d.vy = 0; }
        })
        .attr("transform", d=>`translate(${d.x},${d.y})`);
    });
  }
  
  // Helper to fully restart binding & simulation
  function restart() {
    updateGraph();
  }
  
  // UI CONTROL HANDLERS
  d3.select("#addVertex").on("click", () => {
    const label = document.getElementById("vertexLabel").value.trim() || String(nextId);
    window.visualGraph.addNode(label);
    document.getElementById("vertexLabel").value = "";
  });
  
  d3.select("#addEdge").on("click", () => {
    const src = +document.querySelector("#edgeSrc").value;
    const tgt = +document.querySelector("#edgeTgt").value;
    if (src && tgt && src !== tgt) {
      window.visualGraph.addEdge(src, tgt);
    }
  });
  
  // Enhanced API with comprehensive functions
  window.visualGraph = {
    // Set entire graph
    setGraph: function(newNodes, newLinks) {
      nodes = (newNodes || []).map(n => ({...n}));
      links = (newLinks || []).map(l => ({...l}));
      
      // Update nextId to avoid conflicts
      if (nodes.length > 0) {
        nextId = Math.max(...nodes.map(n => n.id)) + 1;
      }
      
      updateDropdowns();
      restart();
      return this;
    },
  
    // Node operations
    addNode: function(label, id = null, x = null, y = null) {
      const nodeId = id !== null ? id : nextId;
      const nodeLabel = label || String(nodeId);
      
      // Check if node already exists
      if (nodes.find(n => n.id === nodeId)) {
        console.warn(`Node with id ${nodeId} already exists`);
        return this;
      }
      
      // CHANGED: default spawn near center with slight jitter (not fixed)
      if (x === null || y === null) {
        x = width / 2 + jitter(10);
        y = height / 2 + jitter(10);
      }

      const newNode = { id: nodeId, label: nodeLabel, x, y };

      // Only fix position if caller explicitly provided x & y
      if (arguments.length >= 4) { // CHANGED: pin only when x & y were passed
        newNode.fx = x;
        newNode.fy = y;
      }
      
      nodes.push(newNode);
      
      // Update nextId if we used it
      if (id === null) {
        nextId++;
      } else if (nodeId >= nextId) {
        nextId = nodeId + 1;
      }
      
      updateDropdowns();
      restart();
      return this;
    },
  
    deleteNode: function(nodeId) {
      const initialLength = nodes.length;
      nodes = nodes.filter(n => n.id !== nodeId);
      links = links.filter(l => l.source.id !== nodeId && l.target.id !== nodeId);
      
      if (nodes.length < initialLength) {
        updateDropdowns();
        restart();
      }
      return this;
    },
  
    updateNode: function(nodeId, properties) {
      const node = nodes.find(n => n.id === nodeId);
      if (node) {
        Object.assign(node, properties);
        updateDropdowns();
        restart();
      }
      return this;
    },
  
    getNode: function(nodeId) {
      return nodes.find(n => n.id === nodeId) || null;
    },
  
    getNodes: function() {
      return [...nodes];
    },
  
    // Edge operations
    addEdge: function(sourceId, targetId, properties = {}) {
      // Check if both nodes exist
      const sourceNode = nodes.find(n => n.id === sourceId);
      const targetNode = nodes.find(n => n.id === targetId);
      
      if (!sourceNode || !targetNode) {
        console.warn(`Cannot add edge: source (${sourceId}) or target (${targetId}) node not found`);
        return this;
      }
      
      if (sourceId === targetId) {
        console.warn('Self-loops are not supported');
        return this;
      }
      
      // Check if edge already exists
      const existingEdge = links.find(l => 
        (l.source.id === sourceId && l.target.id === targetId) ||
        (l.source.id === targetId && l.target.id === sourceId)
      );
      
      if (existingEdge) {
        console.warn(`Edge between ${sourceId} and ${targetId} already exists`);
        return this;
      }
      
      const newLink = { source: sourceId, target: targetId, ...properties };
      links.push(newLink);
      restart();
      return this;
    },
  
    deleteEdge: function(sourceId, targetId) {
      const initialLength = links.length;
      links = links.filter(l => 
        !((l.source.id === sourceId && l.target.id === targetId) ||
          (l.source.id === targetId && l.target.id === sourceId))
      );
      
      if (links.length < initialLength) {
        restart();
      }
      return this;
    },
  
    getEdge: function(sourceId, targetId) {
      return links.find(l => 
        (l.source.id === sourceId && l.target.id === targetId) ||
        (l.source.id === targetId && l.target.id === sourceId)
      ) || null;
    },
  
    getEdges: function() {
      return [...links];
    },
  
    // Utility functions
    clear: function() {
      nodes = [];
      links = [];
      nextId = 1;
      updateDropdowns();
      restart();
      return this;
    },
  
    getNodeCount: function() {
      return nodes.length;
    },
  
    getEdgeCount: function() {
      return links.length;
    },
  
    // Graph analysis functions
    getNeighbors: function(nodeId) {
      const neighbors = [];
      links.forEach(link => {
        if (link.source.id === nodeId) {
          neighbors.push(link.target.id);
        } else if (link.target.id === nodeId) {
          neighbors.push(link.source.id);
        }
      });
      return [...new Set(neighbors)]; // Remove duplicates
    },
  
    getDegree: function(nodeId) {
      return this.getNeighbors(nodeId).length;
    },
  
    isConnected: function(sourceId, targetId) {
      return !!this.getEdge(sourceId, targetId);
    },
  
    // Batch operations
    addNodes: function(nodeArray) {
      nodeArray.forEach(nodeData => {
        if (typeof nodeData === 'string') {
          this.addNode(nodeData);
        } else {
          this.addNode(nodeData.label, nodeData.id, nodeData.x, nodeData.y);
        }
      });
      return this;
    },
  
    addEdges: function(edgeArray) {
      edgeArray.forEach(edge => {
        this.addEdge(edge.source, edge.target, edge.properties);
      });
      return this;
    },
  
    // Export/Import
    exportGraph: function() {
      return {
        nodes: this.getNodes(),
        links: this.getEdges(),
        nextId: nextId
      };
    },
  
    importGraph: function(graphData) {
      if (graphData.nodes && graphData.links) {
        this.setGraph(graphData.nodes, graphData.links);
        if (graphData.nextId) {
          nextId = graphData.nextId;
        }
      }
      return this;
    },
  
    // Layout controls
    pauseSimulation: function() {
      simulation.stop();
      return this;
    },
  
    resumeSimulation: function() {
      simulation.restart();
      return this;
    },
  
    restartSimulation: function() {
      simulation.alpha(1).restart();
      return this;
    }
  };
  
});

// initial draw
restart();