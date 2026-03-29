"use client";

import React from "react";

interface DictPanelProps {
  entries: Record<string, any> | [string, any][];
}

const normalizeEntries = (entries: DictPanelProps["entries"]): [string, any][] => {
  if (Array.isArray(entries)) return entries as [string, any][];
  if (!entries) return [];
  return Object.entries(entries);
};

const DictPanel: React.FC<DictPanelProps> = ({ entries }) => {
  const items = normalizeEntries(entries);

  return (
    <div className="h-full w-full overflow-auto space-y-2">
      <div className="rounded border" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--panel-content-bg)', transition: 'border-color 0.3s ease, background-color 0.3s ease' }}>
        <table className="min-w-full text-sm">
          <thead style={{ backgroundColor: 'var(--panel-header-bg)', transition: 'background-color 0.3s ease' }}>
            <tr>
              <th className="px-3 py-2 text-left text-xs uppercase" style={{ color: 'var(--foreground)', opacity: 0.6, transition: 'color 0.3s ease' }}>Key</th>
              <th className="px-3 py-2 text-left text-xs uppercase" style={{ color: 'var(--foreground)', opacity: 0.6, transition: 'color 0.3s ease' }}>Value</th>
            </tr>
          </thead>
          <tbody>
            {items.length ? (
              items.map(([k, v], idx) => (
                <tr 
                  key={k}
                  style={{
                    backgroundColor: idx % 2 === 0 ? 'var(--panel-content-bg)' : 'var(--panel-header-bg)',
                    transition: 'background-color 0.3s ease'
                  }}
                >
                  <td className="px-3 py-2 font-mono" style={{ color: 'var(--foreground)', transition: 'color 0.3s ease' }}>{k}</td>
                  <td className="px-3 py-2 font-mono" style={{ color: 'var(--foreground)', transition: 'color 0.3s ease' }}>{JSON.stringify(v)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td className="px-3 py-3 " colSpan={2} style={{ color: 'var(--foreground)', opacity: 0.6, transition: 'color 0.3s ease' }}>
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
