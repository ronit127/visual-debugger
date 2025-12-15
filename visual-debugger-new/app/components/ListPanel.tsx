"use client";

import React from "react";

interface ListPanelProps {
  name: string;
  values: any[];
}

const ListPanel: React.FC<ListPanelProps> = ({ name, values }) => {
  return (
    <div className="h-full w-full overflow-auto space-y-2">
      <div className="text-sm font-semibold text-gray-700">{name}</div>
      <ul className="space-y-1 text-sm">
        {values?.length ? (
          values.map((v, idx) => (
            <li
              key={idx}
              className="flex items-center justify-between rounded border border-gray-200 bg-white px-3 py-2"
            >
              <span className="text-gray-800">Index {idx}</span>
              <span className="font-mono text-gray-900">{JSON.stringify(v)}</span>
            </li>
          ))
        ) : (
          <li className="rounded border border-dashed border-gray-200 px-3 py-2 text-gray-500">
            Empty list
          </li>
        )}
      </ul>
    </div>
  );
};

export default ListPanel;
