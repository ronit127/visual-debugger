"use client";

import React, { useState } from "react";
import CodeEditor from "./components/editor";
import DraggableComponent from "./components/draggable";
// experimenting with React Flow library for connections between editor and draggable components
import { ReactFlow } from "@xyflow/react";
import "@xyflow/react/dist/style.css";

export default function App() {
  const [code, setCode] = useState<string>(
    `// Welcome to Visual Debugger\n// Start typing your Python code here\n`
  );
  // changing between editor and debug modes
  const [mode, setMode] = useState<boolean>(true);

  // will be used for adding nodes
  const handleChange = (value: string) => {
    if (value?.endsWith("\n")) {
      setCode(value + "// placeholder");
    } else {
      setCode(value ?? "");
    }
  };

  const handleClick = () => {
    setMode(!mode);
  };

  return (
    <div className="flex relative h-screen w-screen items-center justify-center">
      {/* React Flow Canvas*/}
      <div className={`absolute inset-0 ${mode ? "z-20" : "z-30"}`}>
        <ReactFlow style={{ width: "100%", height: "100%" }}>
          <DraggableComponent zIndex={40} />
          {/* make draggable component node and experiment with react flow */}
        </ReactFlow>
      </div>
      {/* Editor and stuff */}
      <main
        className={`relative ${
          mode ? "z-30" : "z-20"
        } flex min-h-screen opacity-75 w-full max-w-4xl flex-col items-center justify-start py-12 px-6 bg-white dark:bg-black sm:items-start`}
      >
        <div className="w-full">
          <div className="mb-6">
            <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
              Visual Debugger
            </h1>
            <p className="text-zinc-600 dark:text-zinc-400">
              A simple code editor for now....
            </p>
          </div>

          <CodeEditor
            code={code}
            onChange={handleChange}
            height="70vh"
            zIndex={10}
          />
        </div>
      </main>
      {/* Switch Mode Button */}
      <button
        className={`absolute top-5 right-5 z-50 p-5 rounded-lg ${
          mode ? "bg-sky-500 hover:bg-sky-700" : "bg-red-500 hover:bg-red-700"
        }  hover:cursor-pointer`}
        onClick={handleClick}
      >
        {mode ? "Editor Mode" : "Debug Mode"}
      </button>
      {/* <div className="relative z-30">
        <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
          <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-start py-12 px-6 bg-white dark:bg-black sm:items-start">
            <div className="w-full">
              <div className="mb-6">
                <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
                  Visual Debugger
                </h1>
                <p className="text-zinc-600 dark:text-zinc-400">
                  A simple code editor for now....
                </p>
              </div>

              <CodeEditor
                code={code}
                onChange={handleChange}
                height="70vh"
                zIndex={10}
              />
            </div>
          </main>
        </div>
      </div> */}
    </div>
  );
}
