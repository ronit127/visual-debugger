"use client";

import React, { useState } from "react";
// react-rnd library for draggable, resizeable window
import { Rnd } from "react-rnd";
// dnd-kit library
// import { DndContext, DragEndEvent, DragMoveEvent } from "@dnd-kit/core";
// import { Draggable } from "./Draggable";
// import { Droppable } from "./Droppable";

function DraggableComponent() {
  const [visible, setVisible] = useState(true);
  const [isHovered, setIsHovered] = useState(false);

  if (!visible) return null;

  return (
    <Rnd
      default={{
        x: 0,
        y: 0,
        width: 300,
        height: 200,
      }}
      minHeight="100"
      minWidth="150"
      bounds="window"
      dragHandleClassName="window-title"
      style={{ borderRadius: "10px", overflow: "hidden" }}
    >
      <div
        className="window-title"
        style={{
          display: "flex",
          alignItems: "center",
          height: "32px",
          padding: "0 6px",
          backgroundColor: "#3c3c3cff",
        }}
      >
        <div style={{ display: "flex", gap: "8px" }}>
          {/* close window */}
          <div
            id="close"
            style={{
              width: 12,
              height: 12,
              background: "#ff5f56", // red
              borderRadius: "50%",
              cursor: "pointer",
              color: "grey",
              fontWeight: "bold",
              fontSize: "12px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
            onClick={() => setVisible(false)}
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
          >
            {isHovered ? "x" : ""}
          </div>
        </div>
      </div>
      <div
        style={{
          position: "relative",
          width: "100%",
          height: "100%",
          boxSizing: "border-box",
          padding: "20px",
          background: "#f0f0f0",
          border: "1px solid #ccc",
          color: "black",
        }}
      >
        I&apos;m a draggable, closeable, resizeable window!
      </div>
    </Rnd>
  );
}

export default function App() {
  return <DraggableComponent />;
}

// previosu dnd code (may use later in the future)
// const [isDropped, setIsDropped] = useState(false);
// const [position, setPosition] = useState({ x: 0, y: 0 });
// const draggableMarkup = (
//   <Draggable
//     style={{ transform: `translate(${position.x}px, ${position.y}px)` }}
//   >
//     Drag me
//   </Draggable>
// );
// const handleDragMove = (event: DragMoveEvent) => {
//   const { delta } = event;
//   setPosition((prev) => ({ x: prev.x + delta.x, y: prev.y + delta.y }));
// };
// const handleDragEnd = (event: DragEndEvent) => {
//   if (event.over && event.over.id === "droppable") {
//     setIsDropped(true);
//   }
// };
// return (
//   <DndContext onDragMove={handleDragMove} onDragEnd={handleDragEnd}>
//     {!isDropped ? draggableMarkup : null}
//     <Droppable>{isDropped ? draggableMarkup : "Drop here"}</Droppable>
//   </DndContext>
// );

// import Image from "next/image";

// export default function Home() {
//   return (
//     <div className="flex min-h-screen items-center justify-center bg-zinc-50 font-sans dark:bg-black">
//       <main className="flex min-h-screen w-full max-w-3xl flex-col items-center justify-between py-32 px-16 bg-white dark:bg-black sm:items-start">
//         <Image
//           className="dark:invert"
//           src="/next.svg"
//           alt="Next.js logo"
//           width={100}
//           height={20}
//           priority
//         />
//         <div className="flex flex-col items-center gap-6 text-center sm:items-start sm:text-left">
//           <h1 className="max-w-xs text-3xl font-semibold leading-10 tracking-tight text-black dark:text-zinc-50">
//             To get started, edit the page.tsx file.
//           </h1>
//           <p className="max-w-md text-lg leading-8 text-zinc-600 dark:text-zinc-400">
//             Looking for a starting point or more instructions? Head over to{" "}
//             <a
//               href="https://vercel.com/templates?framework=next.js&utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//               className="font-medium text-zinc-950 dark:text-zinc-50"
//             >
//               Templates
//             </a>{" "}
//             or the{" "}
//             <a
//               href="https://nextjs.org/learn?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//               className="font-medium text-zinc-950 dark:text-zinc-50"
//             >
//               Learning
//             </a>{" "}
//             center.
//           </p>
//         </div>
//         <div className="flex flex-col gap-4 text-base font-medium sm:flex-row">
//           <a
//             className="flex h-12 w-full items-center justify-center gap-2 rounded-full bg-foreground px-5 text-background transition-colors hover:bg-[#383838] dark:hover:bg-[#ccc] md:w-[158px]"
//             href="https://vercel.com/new?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//             target="_blank"
//             rel="noopener noreferrer"
//           >
//             <Image
//               className="dark:invert"
//               src="/vercel.svg"
//               alt="Vercel logomark"
//               width={16}
//               height={16}
//             />
//             Deploy Now
//           </a>
//           <a
//             className="flex h-12 w-full items-center justify-center rounded-full border border-solid border-black/[.08] px-5 transition-colors hover:border-transparent hover:bg-black/[.04] dark:border-white/[.145] dark:hover:bg-[#1a1a1a] md:w-[158px]"
//             href="https://nextjs.org/docs?utm_source=create-next-app&utm_medium=appdir-template-tw&utm_campaign=create-next-app"
//             target="_blank"
//             rel="noopener noreferrer"
//           >
//             Documentation
//           </a>
//         </div>
//       </main>
//     </div>
//   );
// }
