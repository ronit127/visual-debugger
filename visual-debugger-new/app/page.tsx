
"use client";

import React, { useState } from "react";
import CodeEditor from "./components/editor";

export default function App() {
  const [code, setCode] = useState<string>(`// Welcome to Visual Debugger\n// Start typing your Python code here\n`);

  return (
    <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
      <main className="flex min-h-screen w-full max-w-4xl flex-col items-center justify-start py-12 px-6 bg-white dark:bg-black sm:items-start">
        <div className="w-full">
          <div className="mb-6">
            <h1 className="text-3xl font-semibold text-black dark:text-zinc-50">
              Visual Debugger
            </h1>
            <p className="text-zinc-600 dark:text-zinc-400">A simple code editor for now....</p>
          </div>

          <CodeEditor code={code} onChange={setCode} height="70vh" />
        </div>
      </main>
    </div>
  );
}
