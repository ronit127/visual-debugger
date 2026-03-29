import React, { useEffect, useState, useRef } from "react";
import Editor, { OnMount, Monaco } from "@monaco-editor/react";
import type { editor } from "monaco-editor";

type CodeEditorProps = {
  code: string;
  onChange?: (value: string) => void;
  height?: string;
  width?: string;
  highlightedLine?: number | null;
  onSelectionChange?: (selection: { text: string; startLine: number; endLine: number } | null) => void;
};

const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  height = "500px",
  width = "100%",
  highlightedLine = null,
  onSelectionChange,
}) => {
  const [isDark, setIsDark] = useState(true);
  const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
  const monacoRef = useRef<Monaco | null>(null);
  const decorationsRef = useRef<string[]>([]);

  useEffect(() => {
    const checkDarkMode = () => {
      const isDarkMode = document.documentElement.classList.contains("dark");
      setIsDark(isDarkMode);
    };

    checkDarkMode();

    const observer = new MutationObserver(checkDarkMode);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["class"] });

    return () => observer.disconnect();
  }, []);

  // Handle line highlighting
  useEffect(() => {
    if (!editorRef.current || !monacoRef.current) return;

    const editor = editorRef.current;
    const monaco = monacoRef.current;

    // Clear previous decorations
    if (decorationsRef.current.length > 0) {
      decorationsRef.current = editor.deltaDecorations(decorationsRef.current, []);
    }

    // Add new decoration if we have a line to highlight
    if (highlightedLine !== null && highlightedLine > 0) {
      decorationsRef.current = editor.deltaDecorations([], [
        {
          range: new monaco.Range(highlightedLine, 1, highlightedLine, 1),
          options: {
            isWholeLine: true,
            className: "highlighted-line",
            glyphMarginClassName: "highlighted-line-glyph",
            overviewRuler: {
              color: "#3b82f6",
              position: monaco.editor.OverviewRulerLane.Full,
            },
          },
        },
      ]);

      // Scroll to the highlighted line
      editor.revealLineInCenter(highlightedLine);
    }
  }, [highlightedLine]);

  const handleEditorDidMount: OnMount = (editor, monaco) => {
    editorRef.current = editor;
    monacoRef.current = monaco;

    // Selection change listener for AI context
    editor.onDidChangeCursorSelection((e) => {
      const model = editor.getModel();
      if (!model) return;
      const selectedText = model.getValueInRange(e.selection);
      if (selectedText && selectedText.trim().length > 0) {
        onSelectionChange?.({
          text: selectedText,
          startLine: e.selection.startLineNumber,
          endLine: e.selection.endLineNumber,
        });
      } else {
        onSelectionChange?.(null);
      }
    });

    // Add custom CSS for line highlighting
    const styleElement = document.getElementById("monaco-highlight-styles");
    if (!styleElement) {
      const style = document.createElement("style");
      style.id = "monaco-highlight-styles";
      style.textContent = `
        .highlighted-line {
          background-color: rgba(59, 130, 246, 0.3) !important;
        }
        .highlighted-line-glyph {
          background-color: #3b82f6;
          width: 5px !important;
          margin-left: 3px;
        }
      `;
      document.head.appendChild(style);
    }
  };

  return (
    <div>
      <Editor
        height={height}
        width={width}
        defaultLanguage="python"
        value={code}
        onChange={(value) => onChange?.(value || "")}
        theme={isDark ? "vs-dark" : "vs"}
        onMount={handleEditorDidMount}
        options={{
          minimap: { enabled: false },
          fontSize: 16,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
          glyphMargin: true,
        }}
      />
    </div>
  );
};

export default CodeEditor;
