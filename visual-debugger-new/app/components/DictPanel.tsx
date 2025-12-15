"use client";

import React from "react";

interface DictPanelProps {
  name: string;
  entries: Record<string, any> | [string, any][];
}

const normalizeEntries = (entries: DictPanelProps["entries"]): [string, any][] => {
  if (Array.isArray(entries)) return entries as [string, any][];
  if (!entries) return [];
  return Object.entries(entries);
};

const DictPanel: React.FC<DictPanelProps> = ({ name, entries }) => {
  const items = normalizeEntries(entries);

  return (
    <div className="h-full w-full overflow-auto space-y-2">
      <div className="text-sm font-semibold text-gray-700">{name}</div>
      <div className="rounded border border-gray-200 bg-white">
        <table className="min-w-full text-sm">
          <thead className="bg-gray-50 text-left text-xs uppercase text-gray-500">
            <tr>
              <th className="px-3 py-2">Key</th>
              <th className="px-3 py-2">Value</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map(([k, v]) => (
                <tr key={k} className="odd:bg-white even:bg-gray-50">
                  <td className="px-3 py-2 font-mono text-gray-800">{k}</td>
                  <td className="px-3 py-2 font-mono text-gray-900">{JSON.stringify(v)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-3 py-3 text-gray-500" colSpan={2}>
                  Empty dict
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default DictPanel;
