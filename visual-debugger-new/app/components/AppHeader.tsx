
'use client'; 

import React from 'react';

// Define the available data structure options
const dataStructureOptions = [
  { value: 'Graphs', label: 'Graphs' },
  { value: 'Arrays', label: 'Arrays' },
  { value: 'LinkedList', label: 'Linked List' },
];

/**
 * AppHeader Component
 */
interface AppHeaderProps {
  selectedDS: string;
  setSelectedDS: (value: string) => void;
}

const AppHeader: React.FC<AppHeaderProps> = ({ selectedDS, setSelectedDS }) => {
  const handleChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedDS(event.target.value);
  };

  return (
    // Replicates the header styling (dark background, padding, flex layout)
    <header className="flex justify-between items-center p-4 bg-gray-800 shadow-lg text-white w-full">
      {/* Title */}
      <h1 className="text-xl font-semibold">Python Code Editor & Visualizer</h1>
      
      {/* Actions (Dropdown and Buttons) */}
      <div className="flex items-center gap-4">
        
        {/* Dropdown */}
        <div className="flex items-center gap-2">
          <label htmlFor="ds-dropdown" className="text-sm text-gray-300">Choose a Data Structure:</label>
          <select 
            id="ds-dropdown" 
            name="ds-dropdown" 
            value={selectedDS} 
            onChange={handleChange}
            className="p-2 rounded-md bg-gray-700 text-white border border-gray-600 focus:ring-indigo-500 focus:border-indigo-500"
          >
            {dataStructureOptions.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
        
        {/* Buttons */}
        <button 
          id="run-code-btn"
          // Using Tailwind for a purple-like color and hover effect
          className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-md transition duration-150"
        >
          Run Code
        </button>
        <button 
          id="debug-btn"
          className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white font-medium rounded-md transition duration-150"
        >
          Debug
        </button>
      </div>
    </header>
  );
};

export default AppHeader;