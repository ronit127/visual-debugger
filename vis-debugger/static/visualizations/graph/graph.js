// Graph data
let nodes = [];
let links = [];
let nextId = 1;

// SVG & simulation setup
const svg = d3.select("#graphSVG");
const width = +svg.attr("width"), height = +svg.attr("height");

const simulation = d3.forceSimulation(nodes)
  .force("link", d3.forceLink(links).id(d => d.id).distance(100))
  .force("charge", d3.forceManyBody().strength(-300))
  .force("center", d3.forceCenter(width/2, height/2));

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
      .attr("r", 20);

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
        // remove node & its links
        nodes = nodes.filter(n => n.id !== d.id);
        links = links.filter(l => l.source.id !== d.id && l.target.id !== d.id);
        // update selects
        d3.selectAll("#edgeSrc, #edgeTgt").selectAll(`option[value='${d.id}']`).remove();
        // rerun
        restart();
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

    nodeG.selectAll("g.node-group")
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
  const newNode = { id: nextId, label };
  nodes.push(newNode);

  // add to dropdowns
  [ "#edgeSrc", "#edgeTgt" ].forEach(sel => {
    d3.select(sel)
      .append("option")
      .attr("value", nextId)
      .text(label);
  });

  nextId++;
  document.getElementById("vertexLabel").value = "";
  restart();
});

d3.select("#addEdge").on("click", () => {
  const src = +document.querySelector("#edgeSrc").value;
  const tgt = +document.querySelector("#edgeTgt").value;
  if (src && tgt && src !== tgt) {
    links.push({ source: src, target: tgt });
    restart();
  }
});

// initial draw
restart();
