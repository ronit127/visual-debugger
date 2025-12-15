"use client";

import React from "react";

interface HeapPanelProps {
  name: string;
  values: any[];
  operations?: string[];
}

const HeapPanel: React.FC<HeapPanelProps> = ({ name, values = [], operations = [] }) => {
  return (
    <div className="h-full w-full overflow-auto space-y-3">
      <div className="text-sm font-semibold text-gray-700">{name}</div>
      <div className="rounded border border-gray-200 bg-white p-3">
        <div className="text-xs uppercase text-gray-500">Array layout</div>
        <div className="mt-2 grid grid-cols-4 gap-2 text-sm">
          {values.length ? (
            values.map((v, idx) => (
              <div key={idx} className="rounded bg-blue-50 px-2 py-1 text-center text-gray-800">
                {JSON.stringify(v)}
              </div>
            ))
          ) : (
            <div className="col-span-4 text-gray-500">Empty heap</div>
          )}
        </div>
      </div>
      {operations.length > 0 && (
        <div className="rounded border border-gray-200 bg-white p-3 text-sm">
          <div className="text-xs uppercase text-gray-500">Operations</div>
          <ul className="mt-1 space-y-1 text-gray-800">
            {operations.map((op, idx) => (
              <li key={idx} className="rounded bg-gray-50 px-2 py-1">
                {op}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default HeapPanel;
