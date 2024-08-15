// Initialize CodeMirror editors
const queryEditor = CodeMirror.fromTextArea(document.getElementById('query'), {
    mode: 'sparql',
    lineNumbers: true,
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    matchBrackets: true,
});

const queryArgsEditor = CodeMirror.fromTextArea(document.getElementById('query-args'), {
    mode: 'application/json',
    lineNumbers: true,
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    matchBrackets: true,
});

const outputEditor = CodeMirror(document.getElementById('output'), {
    mode: 'sparql', // Adjust this based on what output you expect (e.g., 'sparql', 'json', etc.)
    lineNumbers: true,
    readOnly: true, // Output should be read-only
    foldGutter: true,
    gutters: ["CodeMirror-linenumbers", "CodeMirror-foldgutter"],
    matchBrackets: true,
    theme: "default", // Adjust theme as needed
});

async function loadAndRun() {
    const pyodide = await loadPyodide();
    await pyodide.loadPackage("micropip");

    // Install your wheel from the local server
    await pyodide.runPythonAsync(`
import micropip
await micropip.install('http://localhost:8050/whl/sparql-0.1.4-py3-none-any.whl')
await micropip.install('http://localhost:8050/whl/stl-0.1.0-py3-none-any.whl')
    `);

    // Load examples from examples.json
    const response = await fetch('examples.json');
    const examples = await response.json();

    // Populate example select dropdown
    const exampleSelect = document.getElementById('example-select');
    examples.examples.forEach((example, index) => {
        const option = document.createElement('option');
        option.value = index;
        option.textContent = example.name;
        exampleSelect.appendChild(option);
    });

    // Set up event listener for example select
    exampleSelect.addEventListener('change', (event) => {
        const selectedExampleIndex = parseInt(event.target.value);
        const selectedExample = examples.examples[selectedExampleIndex];
        queryEditor.setValue(selectedExample.query);
        queryArgsEditor.setValue(JSON.stringify(selectedExample.queryArgs, null, 4));
        queryEditor.scrollIntoView();
        queryArgsEditor.scrollIntoView();
    });

    // Set up event listener for run button
    document.getElementById("run-btn").addEventListener("click", async () => {
        const query = queryEditor.getValue();
        const queryArgs = queryArgsEditor.getValue();

        try {
            const result = await pyodide.runPythonAsync(`
from stl import query_rewrite
import json

query = """${query}"""

query_args = ${queryArgs}

result = query_rewrite(query, query_args)
result
            `);

            outputEditor.setValue(result);
        } catch (error) {
            outputEditor.setValue("Error: " + error.message);
        }
    });
}

loadAndRun();