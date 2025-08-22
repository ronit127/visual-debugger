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
      minimap: { enabled: true },
      fontSize: 14,
      automaticLayout: true,
    });
  });

  runButton.addEventListener('click', function () {
    const code = editor.getValue();
    processCode(code);
  });

  async function processCode(code) {
    try {
      outputPlaceholder.style.display = 'none';
      outputResults.innerHTML = 'Processing...';
      outputResults.style.display = 'block';

      fetch('/add_data', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: code }),
      })
        .then((res) => res.json())
        .then((data) => console.log(data));

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
    if (
      data.graph &&
      window.visualGraph &&
      typeof window.visualGraph.setGraph === 'function'
    ) {
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