document.addEventListener('DOMContentLoaded', function() {
    
    const runButton = document.getElementById('run-code-btn');
    const outputResults = document.getElementById('output-results');
    const outputPlaceholder = document.getElementById('output-placeholder');
    //need to add more elements

    const defaultCode = 'def hello_world():\n    print("Hello, world!")\n    x = 5\n    y = 10\n    return x + y\n\nhello_world()';
    
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
                outputResults.innerHTML = `
                    <h3>Output:</h3>
                    <pre>${data.output}</pre>
                `;
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
    
    // EXTENSION POINT 3:
    // Functions for visualization can be added here
    // function createVisualization(data) {
    //     // D3.js visualization code would go here
    // }
});