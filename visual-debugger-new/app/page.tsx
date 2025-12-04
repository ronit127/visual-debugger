'use client'; // Required for using useState Hook

import React, { useState } from 'react';
import AppHeader from './components/AppHeader'; // Import the new header component

export default function Home() {
  // 1. STATE: Manages the selected data structure. 
  // We need this state here because the header needs to read it, and later, the visualizer will too.
  const [selectedDS, setSelectedDS] = useState('Graphs'); // Default value

  return (
    // The outer container for the whole application
    <div className="flex flex-col min-h-screen bg-gray-900 font-sans">
      
      {}
      <AppHeader 
        selectedDS={selectedDS} 
        setSelectedDS={setSelectedDS} 
      />
      
      {}
      <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black w-full">
        <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
          <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
            <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
              Visual Debugger Test
            </h1>
            <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
              Purely for testing purposes. 
              Currently selected: {selectedDS}
            </p>
          </div>
        </main>
      </div>
    </div>
  );
}