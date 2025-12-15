# Visual Debugger

A real-time Python code visualization and debugging tool that transforms complex data structures into interactive, animated visualizations. Write Python code and instantly see graphs, lists, heaps, and dictionaries animate as your code executes.

## Features

- **Interactive Code Editor** - Write and execute Python code with syntax highlighting
- **Real-time Visualization** - Watch data structures update dynamically as code runs
- **Multiple Data Structure Views**:
  - Graph visualization with node and edge rendering
  - List/array views with indexed elements
  - Heap structure with binary tree visualization
  - Dictionary/hash map displays with key-value pairs
  - Execution logs and console output
- **Resizable Panels** - Customize your workspace layout on the fly
- **Operation Tracking** - See the sequence of operations as they happen

## Tech Stack

**Frontend:**
- Next.js 16 (React 19)
- TypeScript
- Tailwind CSS
- Monaco Editor for code editing
- D3.js for graph visualization
- React Flow for interactive diagrams
- React RnD for resizable/draggable components

**Backend:**
- Flask with Python 3.8+
- Dynamic code execution with operation tracking
- CORS-enabled API

## Getting Started

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd visual-debugger
```

2. Install frontend dependencies:
```bash
npm install
```

3. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Running Locally

1. Start the backend server (from the `backend` directory):
```bash
python app.py
```
The Flask server runs on `http://localhost:5000`

2. In a new terminal, start the Next.js development server:
```bash
npm run dev
```
Open [http://localhost:3000](http://localhost:3000) in your browser

3. Write Python code in the editor and click "Run" to visualize your data structures

## Project Structure

```
visual-debugger/
├── app/
│   ├── api/               # Next.js API routes
│   ├── components/        # Reusable React components
│   │   ├── editor.tsx     # Code editor component
│   │   ├── Graph.tsx      # Graph visualization
│   │   ├── ListPanel.tsx  # List view
│   │   ├── HeapPanel.tsx  # Heap structure view
│   │   ├── DictPanel.tsx  # Dictionary view
│   │   ├── LogPanel.tsx   # Log output
│   │   └── draggable.tsx  # Resizable panel wrapper
│   ├── types/             # TypeScript type definitions
│   ├── page.tsx           # Main application component
│   └── globals.css        # Global styles
├── backend/
│   ├── app.py             # Flask application and core logic
│   └── requirements.txt    # Python dependencies
└── public/                # Static assets
```

## How It Works

1. User writes Python code in the Monaco editor
2. Code is sent to the Flask backend via API
3. Backend executes code with instrumentation to track data structure operations
4. Operations (node creation, insertions, deletions) are captured and returned
5. Frontend renders interactive visualizations that animate through operations
6. Multiple data structures can be visualized simultaneously in draggable panels

## Example Usage

```python
# Create and visualize a simple graph
graph = Graph()
graph.add_node(1)
graph.add_node(2)
graph.add_edge(1, 2)

# Or work with lists
arr = [3, 1, 4, 1, 5, 9]
arr.sort()

# Or dictionaries
data = {"name": "Alice", "age": 30, "city": "NYC"}
```

Each operation updates the visualization in real-time.

## Development

### Scripts
- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

### Architecture Notes

- **Frontend State Management**: React hooks manage editor code, panels, and visualization data
- **Backend Processing**: Python AST analysis and code instrumentation for operation tracking
- **Communication**: REST API for code execution and result retrieval
- **Visualization**: D3.js for graphs, custom components for other data structures

## Future Enhancements

- Algorithm step-through with breakpoints
- Performance metrics and complexity analysis
- Export visualizations as images/videos
- Collaborative debugging sessions
- Support for additional data structures (trees, tries, graphs with weighted edges)

## License

MIT

## Contact

For questions or feedback, please open an issue in the repository.
