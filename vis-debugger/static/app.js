document.addEventListener('DOMContentLoaded', function() {
    
  const runButton = document.getElementById('run-code-btn');
  const outputResults = document.getElementById('output-results');
  const outputPlaceholder = document.getElementById('output-placeholder');
  //need to add more elements

  const defaultCode = 'import networkx as nx\n     \n# Create a graph\nG = nx.Graph()\n\n# Add nodes\nG.add_node(1)\nG.add_nodes_from([2, 3, 4])\n\n# Add edges\nG.add_edge(1, 2)\nG.add_edges_from([(2, 3), (3, 4)])\n\n# Remove a node\nG.remove_node(4)\n\n# Remove an edge\nG.remove_edge(1, 2)';
  
  let editor;    
  require(['vs/editor/editor.main'], function() {
      editor = monaco.editor.create(document.getElementById('monaco-editor'), {
          value: defaultCode,
          language: 'python',
          theme: 'vs-dark',
          lineNumbers: 'on',
          scrollBeyondLastLine: false,
          minimap: { enabled: true },
          fontSize: 14,
          automaticLayout: true
      });
      
  });
  
  // when we click the run button, we want to run the code (to process the output)
  runButton.addEventListener('click', function() {
      const code = editor.getValue();
      processCode(code);
  });
  
  // this js function is used to process the code
  async function processCode(code) {
      try {
          // Show loading state
          outputPlaceholder.style.display = 'none';
          outputResults.innerHTML = 'Processing...';
          outputResults.style.display = 'block';
          
          // Send code to backend
          const response = await fetch('/api/run', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' }, //signals the data being sent is JSON
              body: JSON.stringify({ code })
          });
          
          // Parse response
          const data = await response.json();
          
          updateVisualization(data);
          if (data.status === 'success') {
              let outputHTML = `
                  <h3>Output:</h3>
                  <pre>${data.output}</pre>
              `;
              
              // Add graph operations if present
              if (data.graph_operations && data.graph_operations.length > 0) {
                  outputHTML += `
                      <h3>Graph Operations:</h3>
                      <div class="graph-operations">
                  `;
                  
                  data.graph_operations.forEach(operation => {
                      outputHTML += `<div class="graph-operation">${operation}</div>`;
                  });
                  
                  outputHTML += `</div>`;
              }
              
              outputResults.innerHTML = outputHTML;
          } else {
              outputResults.innerHTML = `
                  <h3>Error:</h3>
                  <pre class="error">${data.error}</pre>
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
  }
  // EXTENSION POINT 2:
  // Add window resize handler
  window.addEventListener('resize', function() {
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

  // Toggle debug menu
  debugBtn.addEventListener('click', function() {
      debugMenu.style.display = 'block';
  });

  closeDebugBtn.addEventListener('click', function() {
      debugMenu.style.display = 'none';
  });

  // Placeholder functionality for debug buttons
  debugStepBtn.addEventListener('click', function() {
      outputResults.style.display = 'block';
      outputResults.innerHTML += '<p>Debug: Step executed</p>';
  });

  debugStepOverBtn.addEventListener('click', function() {
      outputResults.style.display = 'block';
      outputResults.innerHTML += '<p>Debug: Step Over executed</p>';
  });

  debugStepIntoBtn.addEventListener('click', function() {
      outputResults.style.display = 'block';
      outputResults.innerHTML += '<p>Debug: Step Into executed</p>';
  });

  debugContinueBtn.addEventListener('click', function() {
      outputResults.style.display = 'block';
      outputResults.innerHTML += '<p>Debug: Continue execution</p>';
  });

  debugStopBtn.addEventListener('click', function() {
      outputResults.style.display = 'block';
      outputResults.innerHTML += '<p>Debug: Execution stopped</p>';
  });
});


// EXTENSION POINT 3:
  // Functions for visualization can be added here
  // function createVisualization(data) {
  //     // D3.js visualization code would go here
  // }
      // Debug functionality