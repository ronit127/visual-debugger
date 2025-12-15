"use client";

import React from "react";

interface LogPanelProps {
  title?: string;
  lines: string[];
}

const LogPanel: React.FC<LogPanelProps> = ({ title = "Logs", lines }) => {
  return (
    <div className="h-full w-full overflow-auto space-y-2">
      <div className="text-sm font-semibold text-gray-700">{title}</div>
      <div className="rounded border border-gray-200 bg-black p-3 font-mono text-xs text-green-200">
        {lines?.length ? (
          lines.map((l, idx) => (
            <div key={idx} className="whitespace-pre-wrap">
              {l}
            </div>
          ))
        ) : (
          <div className="text-gray-400">No log entries</div>
        )}
      </div>
    </div>
  );
};

export default LogPanel;
