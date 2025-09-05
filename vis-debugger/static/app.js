document.addEventListener('DOMContentLoaded', function () {
  const runButton = document.getElementById('run-code-btn');
  const outputResults = document.getElementById('output-results');
  const outputPlaceholder = document.getElementById('output-placeholder');

  const defaultCode =
    'import networkx as nx\n     \n# Create a graph\nG = nx.Graph()\n\n# Add nodes\nG.add_node(1)\nG.add_nodes_from([2, 3, 4])\n\n# Add edges\nG.add_edge(1, 2)\nG.add_edges_from([(2, 3), (3, 4)])\n\n# Remove a node\nG.remove_node(4)\n\n# Remove an edge\nG.remove_edge(1, 2)';

  let editor;
  require(['vs/editor/editor.main'], function () {
    editor = monaco.editor.create(document.getElementById('monaco-editor'), {
      value: defaultCode,
      language: 'python',
      theme: 'vs-dark',
      lineNumbers: 'on',
      scrollBeyondLastLine: false,
      minimap: { enabled: false },
      fontSize: 19,
      automaticLayout: true,
    });
  });

  runButton.addEventListener('click', function () {
    const code = editor.getValue();
    processCode(code);
  });

  async function processCode(code) {
    try {
      outputPlaceholder.style.display = 'none'; // hide the placeholder text
      outputResults.innerHTML = 'Processing...';  
      outputResults.style.display = 'block';

      // TODO: add user code to MongoDB (cloud save)
      fetch('/add_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code }),
      })
        .then((res) => res.json())
        .then((data) => console.log(data));

       // send code to the backend for processing
      const response = await fetch('/api/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code }),
      });

      const data = await response.json();
      updateVisualization(data);
      if (data.status === 'success') {
        let outputHTML = `
          <h3>Output:</h3>
          <pre>${data.output}</pre>
        `;

        if (data.graph_operations && data.graph_operations.length > 0) {
          outputHTML += `
            <div style="margin-top: 1.5rem;"></div>
            <h3>Graph Operations:</h3>
            <div class="graph-operations">
          `;

          data.graph_operations.forEach((operation) => {
            outputHTML += `<div class="graph-operation">${operation}</div>`;
          });

          outputHTML += `</div>`;
        }

        outputResults.innerHTML = outputHTML;
      } else {
        outputResults.innerHTML = `
          <h3>Error:</h3>
          <pre class="error">${data.status}</pre>
        `;
      }
    } catch (err) {
      outputResults.innerHTML = `
        <h3>Error:</h3>
        <pre class="error">Failed to process code: ${err.message}</pre>
      `;
    }
  }

  function updateVisualization(data) {
    if (!data) return;
    
    console.log("Updating visualization with data:", data);
    
    if (window.visualGraph && typeof window.visualGraph.clear === 'function') {
      window.visualGraph.clear();
    }
    
    const addedNodes = new Set();
    
    let graphNameGlobal = ""
    // Process graph operations to build the graph dynamically
    if (window.visualGraph && Array.isArray(data.graph_operations)) {
      console.log("Processing graph operations:", data.graph_operations);
      
      data.graph_operations.forEach((operation, index) => {
        console.log(`Processing operation ${index}:`, operation);
        
        if (typeof operation !== "string") return;
  
        if (operation.includes("Graph created:")) {
          // Graph creation - graph is already cleared above
          console.log("Graph created, starting fresh");
          
        } else if (operation.includes("Node added with value:")) {
          // Updated regex to handle graph name prefix
          const match = operation.match(/Graph '(.+?)': Node added with value: (.+)$/);
          if (match) {
            const graphName = match[1];

            if (graphNameGlobal == ""){
              graphNameGlobal = graphName;
            }
            else if (graphNameGlobal == graphName){
              const nodeValue = match[2].trim();
              console.log(`Adding node: ${nodeValue}`);
              
              // Use nodeValue as both ID and label, convert to number if possible
              let nodeId = nodeValue;
              try {
                const numericId = parseInt(nodeValue);
                if (!isNaN(numericId)) {
                  nodeId = numericId;
                }
              } catch (e) {
                // Keep as string if not numeric
              }
              
              if (!addedNodes.has(nodeId)) {
                window.visualGraph.addNode(nodeValue, nodeId);
                addedNodes.add(nodeId);
              }
            }
          }
          
        } else if (operation.includes("Edge added between")) {
          const match = operation.match(/Graph '(.+?)': Edge added between (.+) and (.+)$/);
          if (match) {
            const graphName = match[1];
            const node1 = match[2].trim();
            const node2 = match[3].trim();
            console.log(`Adding edge between: ${node1} and ${node2}`);
          
            if (graphNameGlobal == ""){
              graphNameGlobal = graphName;
            }
            else if (graphNameGlobal == graphName){
              let nodeId1 = node1;
              let nodeId2 = node2;
              try {
                const num1 = parseInt(node1);
                const num2 = parseInt(node2);
                if (!isNaN(num1)) nodeId1 = num1;
                if (!isNaN(num2)) nodeId2 = num2;
              } catch (e) {
                // Keep as strings if not numeric
              }
              
              // Make sure both nodes exist before adding edge
              if (!addedNodes.has(nodeId1)) {
                window.visualGraph.addNode(node1, nodeId1);
                addedNodes.add(nodeId1);
              }
              if (!addedNodes.has(nodeId2)) {
                window.visualGraph.addNode(node2, nodeId2);
                addedNodes.add(nodeId2);
              }
              
              window.visualGraph.addEdge(nodeId1, nodeId2);
            }
          }
          
        } else if (operation.includes("Node removed with value:")) {
          // Updated regex to handle graph name prefix
          const match = operation.match(/Graph '(.+?)': Node removed with value: (.+)$/);
          if (match) {
            const graphName = match[1];
            const nodeValue = match[2].trim();
            console.log(`Removing node: ${nodeValue}`);
            
            if (graphNameGlobal == ""){
              graphNameGlobal = graphName;
            }
            else if (graphNameGlobal == graphName){
              // Convert to number if possible for consistency
              let nodeId = nodeValue;
              try {
                const numericId = parseInt(nodeValue);
                if (!isNaN(numericId)) {
                  nodeId = numericId;
                }
              } catch (e) {
                // Keep as string if not numeric
              }
              
              window.visualGraph.deleteNode(nodeId);
              addedNodes.delete(nodeId);
            }
          }
          
        } else if (operation.includes("Edge removed between")) {
          const match = operation.match(/Graph '(.+?)': Edge removed between (.+) and (.+)$/);
          if (match) {
            const graphName = match[1];
            const node1 = match[2].trim();
            const node2 = match[3].trim();
            console.log(`Removing edge between: ${node1} and ${node2}`);
            
            if (graphNameGlobal == ""){
              graphNameGlobal = graphName;
            }
            else if (graphNameGlobal == graphName){
              let nodeId1 = node1;
              let nodeId2 = node2;
              try {
                const num1 = parseInt(node1);
                const num2 = parseInt(node2);
                if (!isNaN(num1)) nodeId1 = num1;
                if (!isNaN(num2)) nodeId2 = num2;
              } catch (e) {
                // Keep as strings if not numeric
              }
              window.visualGraph.deleteEdge(nodeId1, nodeId2);
            }
          }
        }
      });
      
      console.log(`Visualization updated. Total nodes: ${window.visualGraph.getNodeCount()}, Total edges: ${window.visualGraph.getEdgeCount()}`);
    }
    
    // Fallback: if no operations or visualGraph not available, use setGraph
    else if (data.graph && window.visualGraph && typeof window.visualGraph.setGraph === 'function') {
      console.log("Using fallback setGraph method");
      window.visualGraph.setGraph(data.graph.nodes, data.graph.links);
    }
  }

  window.addEventListener('resize', function () {
    if (editor) {
      editor.layout();
    }
  });

  const debugBtn = document.getElementById('debug-btn');
  const debugMenu = document.getElementById('debug-menu');
  const closeDebugBtn = document.getElementById('close-debug-btn');
  const debugStepBtn = document.getElementById('debug-step-btn');
  const debugStepOverBtn = document.getElementById('debug-step-over-btn');
  const debugStepIntoBtn = document.getElementById('debug-step-into-btn');
  const debugContinueBtn = document.getElementById('debug-continue-btn');
  const debugStopBtn = document.getElementById('debug-stop-btn');

  debugBtn.addEventListener('click', function () {
    debugMenu.style.display = 'block';
  });

  closeDebugBtn.addEventListener('click', function () {
    debugMenu.style.display = 'none';
  });

  debugStepBtn.addEventListener('click', function () {
    outputResults.style.display = 'block';
    outputResults.innerHTML += '<p>Debug: Step executed</p>';
  });

  debugStepOverBtn.addEventListener('click', function () {
    outputResults.style.display = 'block';
    outputResults.innerHTML += '<p>Debug: Step Over executed</p>';
  });

  debugStepIntoBtn.addEventListener('click', function () {
    outputResults.style.display = 'block';
    outputResults.innerHTML += '<p>Debug: Step Into executed</p>';
  });

  debugContinueBtn.addEventListener('click', function () {
    outputResults.style.display = 'block';
    outputResults.innerHTML += '<p>Debug: Continue execution</p>';
  });

  debugStopBtn.addEventListener('click', function () {
    outputResults.style.display = 'block';
    outputResults.innerHTML += '<p>Debug: Execution stopped</p>';
  });
});