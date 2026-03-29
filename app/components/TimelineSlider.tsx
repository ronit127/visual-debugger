"use client";

import React, { useCallback, useEffect, useRef } from "react";
import { FaChevronLeft, FaChevronRight, FaTimes, FaExchangeAlt, FaLevelUpAlt, FaLevelDownAlt, FaCode } from "react-icons/fa";
import { TimelineEvent } from "../types/backend";

interface TimelineSliderProps {
  timeline: TimelineEvent[];
  currentStep: number;
  onStepChange: (step: number) => void;
  onClose: () => void;
}

const TimelineSlider: React.FC<TimelineSliderProps> = ({
  timeline,
  currentStep,
  onStepChange,
  onClose,
}) => {
  const sliderRef = useRef<HTMLInputElement>(null);

  // Filter out "line" events and create a mapping for steps
  const filteredTimeline = timeline.filter(e => e.event !== "line");
  const stepMapping = filteredTimeline.map(e => e.step);
  const maxStepFiltered = filteredTimeline.length;
  const minStepFiltered = maxStepFiltered > 0 ? 1 : 0;

  // Map currentStep to filtered index
  const currentFilteredStep = stepMapping.indexOf(currentStep) + 1;

  const maxStep = timeline.length > 0 ? timeline[timeline.length - 1].step : 0;
  const minStep = timeline.length > 0 ? timeline[0].step : 0;

  // Get current event info from original timeline
  const currentEvent = timeline.find((e) => e.step === currentStep);

  const handleSliderChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const newFilteredStep = parseInt(e.target.value, 10);
      const originalStep = stepMapping[newFilteredStep - 1];
      if (originalStep !== undefined) {
        onStepChange(originalStep);
      }
    },
    [onStepChange, stepMapping]
  );

  const handleStepForward = useCallback(() => {
    if (currentFilteredStep < maxStepFiltered) {
      const nextFilteredStep = currentFilteredStep + 1;
      const originalStep = stepMapping[nextFilteredStep - 1];
      onStepChange(originalStep);
    }
  }, [currentFilteredStep, maxStepFiltered, onStepChange, stepMapping]);

  const handleStepBackward = useCallback(() => {
    if (currentFilteredStep > minStepFiltered) {
      const prevFilteredStep = currentFilteredStep - 1;
      const originalStep = stepMapping[prevFilteredStep - 1];
      onStepChange(originalStep);
    }
  }, [currentFilteredStep, minStepFiltered, onStepChange, stepMapping]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }
      switch (e.key) {
        case "ArrowRight":
          e.preventDefault();
          handleStepForward();
          break;
        case "ArrowLeft":
          e.preventDefault();
          handleStepBackward();
          break;
        case "Home":
          e.preventDefault();
          if (stepMapping.length > 0) {
            onStepChange(stepMapping[0]);
          }
          break;
        case "End":
          e.preventDefault();
          if (stepMapping.length > 0) {
            onStepChange(stepMapping[stepMapping.length - 1]);
          }
          break;
        case "Escape":
          e.preventDefault();
          onClose();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleStepForward, handleStepBackward, onStepChange, onClose, stepMapping]);

  const getEventSummary = (event: TimelineEvent | undefined): { icon: React.ReactNode; text: string } => {
    if (!event) return { icon: <FaCode size={12} />, text: "" };
    if (event.event === "call") {
      return { icon: <FaLevelDownAlt size={12} />, text: `call ${event.func ?? ""}`.trim() };
    }
    if (event.event === "return") {
      return { icon: <FaLevelUpAlt size={12} />, text: `return ${event.func ?? ""}`.trim() };
    }
    if (event.event === "mutation") {
      const details = [event.op, event.var].filter(Boolean).join(" • ");
      return { icon: null, text: details };
    }
    if (event.event === "exception") {
      return { icon: <FaCode size={12} />, text: event.op ?? "exception" };
    }
    if (event.event === "line") {
      return { icon: <FaCode size={12} />, text: "" };
    }
    return { icon: <FaCode size={12} />, text: event.line != null ? `line ${event.line}` : "line" };
  };

  if (timeline.length === 0) {
    return (
      <div
        className="timeline-slider-container"
        style={{
          position: "fixed",
          bottom: "16px",
          left: "50%",
          transform: "translateX(-50%)",
          backgroundColor: "var(--subtle-bg)",
          border: "1px solid var(--border)",
          borderRadius: "10px",
          padding: "10px 12px",
          zIndex: 1000,
          boxShadow: "0 10px 20px rgba(0, 0, 0, 0.25)",
        }}
      >
        <div className="flex items-center gap-3">
          <span className="text-xs" style={{ color: "var(--foreground)", opacity: 0.8 }}>
            No timeline data
          </span>
          <button
            onClick={onClose}
            className="p-2 rounded hover:opacity-80"
            style={{ backgroundColor: "transparent", color: "var(--foreground)" }}
            aria-label="Close timeline"
          >
            <FaTimes size={12} />
          </button>
        </div>
      </div>
    );
  }

  return (
    <div
      className="timeline-slider-container"
      style={{
        position: "fixed",
        bottom: "16px",
        left: "50%",
        transform: "translateX(-50%)",
        backgroundColor: "var(--subtle-bg)",
        border: "1px solid var(--border)",
        borderRadius: "10px",
        padding: "10px 12px",
        zIndex: 1000,
        boxShadow: "0 1px 3px rgba(0, 0, 0, 0.25)",
        minWidth: "520px",
        maxWidth: "90vw",
      }}
    >
      <div className="flex items-center gap-2">
        <button
          onClick={handleStepBackward}
          disabled={currentFilteredStep <= minStepFiltered}
          className={`p-2 rounded hover:opacity-80 disabled:opacity-40 ${currentFilteredStep > minStepFiltered ? "hover:cursor-pointer" : ""}`}
          style={{ backgroundColor: "transparent", color: "var(--foreground)" }}
          aria-label="Previous step"
        >
          <FaChevronLeft size={14} />
        </button>

        <input
          ref={sliderRef}
          type="range"
          min={minStepFiltered}
          max={maxStepFiltered}
          value={currentFilteredStep}
          onChange={handleSliderChange}
          className="timeline-range-slider flex-1"
          style={{
            cursor: "pointer",
            "--progress": `${maxStepFiltered > 0 ? ((currentFilteredStep - minStepFiltered) / (maxStepFiltered - minStepFiltered)) * 100 : 0}%`,
          } as React.CSSProperties}
        />

        <button
          onClick={handleStepForward}
          disabled={currentFilteredStep >= maxStepFiltered}
          className={`p-2 rounded hover:opacity-80 disabled:opacity-40 ${currentFilteredStep < maxStepFiltered ? "hover:cursor-pointer" : ""}`}
          style={{ backgroundColor: "transparent", color: "var(--foreground)" }}
          aria-label="Next step"
        >
          <FaChevronRight size={14} />
        </button>

        <button
          onClick={onClose}
          className="p-1 rounded hover:opacity-80 hover:cursor-pointer"
          style={{ backgroundColor: "transparent", color: "var(--foreground)" }}
          aria-label="Close timeline"
        >
          <FaTimes size={14} />
        </button>
      </div>

      <div className="mt-2 mr-1 flex items-center justify-between gap-3">
        <div style={{ width: "60px" }}></div>
        <div className="flex items-center gap-2 mr-5 " style={{ color: "var(--foreground)", opacity: 0.85 }}>
          {getEventSummary(currentEvent).icon}
          <span className="text-sm" style={{ letterSpacing: "-0.02em" }}>
            {getEventSummary(currentEvent).text}
          </span>
        </div>
        {currentEvent?.line != null ? (
          <span 
            className="text-sm"
            style={{ 
              width: "60px",
              textAlign: "right",
              color: "var(--foreground)"
              , opacity: 0.85 
            }}
          >
            line {currentEvent.line}
          </span>
        ) : (
          <div style={{ width: "60px" }}></div>
        )}
      </div>
    </div>
  );
};

export default TimelineSlider;
