"use client";

import React from "react";

interface HeapPanelProps {
  values: any[];
  operations?: string[];
}

const HeapPanel: React.FC<HeapPanelProps> = ({ values = [], operations = [] }) => {
  return (
    <div className="h-full w-full overflow-auto space-y-3">
      <div className="rounded border p-3" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--panel-content-bg)', transition: 'border-color 0.3s ease, background-color 0.3s ease' }}>
        <div className="text-xs uppercase" style={{ color: 'var(--foreground)', opacity: 0.6, transition: 'color 0.3s ease' }}>Array layout</div>
        <div className="mt-2 grid grid-cols-4 gap-2 text-sm">
          {values.length ? (
            values.map((v, idx) => (
              <div 
                key={idx} 
                className="rounded px-2 py-1 text-center"
                style={{
                  backgroundColor: 'var(--segment-bg)',
                  color: 'var(--foreground)',
                  transition: 'background-color 0.3s ease, color 0.3s ease'
                }}
              >
                {JSON.stringify(v)}
              </div>
            ))
          ) : (
            <div className="col-span-4" style={{ color: 'var(--foreground)', opacity: 0.6, transition: 'color 0.3s ease' }}>Empty heap</div>
          )}
        </div>
      </div>
      {operations.length > 0 && (
        <div className="rounded border p-3 text-sm" style={{ borderColor: 'var(--border)', backgroundColor: 'var(--panel-content-bg)', transition: 'border-color 0.3s ease, background-color 0.3s ease' }}>
          <div className="text-xs uppercase" style={{ color: 'var(--foreground)', opacity: 0.6, transition: 'color 0.3s ease' }}>Operations</div>
          <ul className="mt-1 space-y-1">
            {operations.map((op, idx) => (
              <li 
                key={idx} 
                className="rounded px-2 py-1"
                style={{
                  backgroundColor: 'var(--subtle-bg)',
                  color: 'var(--foreground)',
                  transition: 'background-color 0.3s ease, color 0.3s ease'
                }}
              >
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
