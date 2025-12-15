import React from "react";
import Editor from "@monaco-editor/react";

type CodeEditorProps = {
  code: string;
  onChange?: (value: string) => void;
  height?: string;
  width?: string;
  zIndex?: number;
};

const CodeEditor: React.FC<CodeEditorProps> = ({
  code,
  onChange,
  height = "500px",
  width = "100%",
  zIndex,
}) => {
  return (
    <div
      className="rounded-xl overflow-hidden border border-gray-300 shadow-sm"
      style={{ position: "relative", zIndex }}
    >
      <Editor
        height={height}
        width={width}
        defaultLanguage="python"
        value={code}
        onChange={(value) => onChange?.(value || "")}
        theme="vs-light"
        options={{
          minimap: { enabled: false },
          fontSize: 14,
          scrollBeyondLastLine: false,
          automaticLayout: true,
          tabSize: 2,
        }}
      />
    </div>
  );
};

export default CodeEditor;
