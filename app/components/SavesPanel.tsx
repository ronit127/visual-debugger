"use client";

import React from "react";
import { FiX, FiDownload } from "react-icons/fi";

interface SavedSession {
  id: string;
  code: string;
  timestamp: number;
  title?: string;
}

interface SavesPanelProps {
  isOpen: boolean;
  onClose: () => void;
  saves: SavedSession[];
  onLoadSave: (code: string) => void;
}

const SavesPanel: React.FC<SavesPanelProps> = ({ isOpen, onClose, saves, onLoadSave }) => {
  if (!isOpen) return null;

  const formatTimestamp = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleString();
  };

  const handleLoadSave = (code: string) => {
    onLoadSave(code);
    onClose();
  };

  return (
    <div
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={onClose}
    >
      <div
        className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Saved Sessions ({saves.length})
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
            aria-label="Close saves panel"
          >
            <FiX size={20} />
          </button>
        </div>

        <div className="overflow-y-auto max-h-[60vh]">
          {saves.length === 0 ? (
            <div className="p-8 text-center text-gray-500 dark:text-gray-400">
              <FiDownload size={48} className="mx-auto mb-4 opacity-50" />
              <p className="text-lg">No saved sessions yet</p>
              <p className="text-sm">Use the save button to save your code</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200 dark:divide-gray-700">
              {saves
                .sort((a, b) => b.timestamp - a.timestamp) // Most recent first
                .map((save) => (
                  <div key={save.id} className="p-4 hover:bg-gray-50 dark:hover:bg-gray-700/50">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-sm font-medium text-gray-900 dark:text-white">
                            Session {save.id.slice(-8)}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {formatTimestamp(save.timestamp)}
                          </span>
                        </div>
                        <div className="text-xs text-gray-600 dark:text-gray-300 mb-2">
                          {save.code.split('\n').length} lines • {save.code.length} characters
                        </div>
                      </div>
                      <button
                        onClick={() => handleLoadSave(save.code)}
                        className="px-3 py-1.5 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-md transition-colors flex items-center gap-1"
                        title="Load this saved code"
                      >
                        <FiDownload size={14} />
                        Load
                      </button>
                    </div>
                    <div className="bg-gray-100 dark:bg-gray-900 rounded-md p-3 overflow-x-auto">
                      <pre className="text-xs text-gray-800 dark:text-gray-200 whitespace-pre-wrap font-mono">
                        {save.code.length > 500
                          ? save.code.slice(0, 500) + '...'
                          : save.code
                        }
                      </pre>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default SavesPanel;
