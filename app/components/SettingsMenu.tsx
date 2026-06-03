"use client";

import React, { useEffect, useState } from "react";
import { FiSettings, FiMoon, FiSun, FiChevronRight } from "react-icons/fi";
import { GoCheck } from "react-icons/go";
const SettingsMenu: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [submenu, setSubmenu] = useState<string | null>(null);
  const [dark, setDark] = useState(() => {
    try {
      const stored = window.localStorage?.getItem("prefers-dark");
      if (stored !== null) return stored === "true";
      return (
        window.matchMedia &&
        window.matchMedia("(prefers-color-scheme: dark)").matches
      );
    } catch (e) {
      return false;
    }
  });

  useEffect(() => {
    try {
      window.localStorage?.setItem("prefers-dark", dark ? "true" : "false");
    } catch (e) {}
    if (dark) {
      document.body.classList.add("dark");
      document.documentElement.classList.add("dark");
    } else {
      document.body.classList.remove("dark");
      document.documentElement.classList.remove("dark");
    }
  }, [dark]);

  const handleModeChange = (mode: "light" | "dark" | "system") => {
    if (mode === "system") {
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setDark(prefersDark);
    } else {
      setDark(mode === "dark");
    }
    setSubmenu(null);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="p-2 rounded-lg hover:opacity-80 transition-opacity"
        style={{
          backgroundColor: "var(--subtle-bg)",
          color: "var(--text)",
          border: "1px solid var(--border)",
          cursor: "pointer",
        }}
        aria-label="Settings"
      >
        <FiSettings size={20} />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-2 w-48 rounded-lg shadow-lg z-10000 overflow-hidden"
          style={{
            backgroundColor: "var(--subtle-bg)",
            border: "1px solid var(--border)",
          }}
        >
          {/* Appearance Menu Item */}
          <button
            onClick={() => setSubmenu(submenu === "appearance" ? null : "appearance")}
            className="w-full px-4 py-3 border-b text-left hover:opacity-80 transition-opacity flex items-center justify-between"
            style={{
              borderColor: "var(--border)",
              color: "var(--text)",
              cursor: "pointer",
            }}
          >
            <div className="flex items-center gap-2">
              <FiSun size={16} />
              <span className="text-sm font-semibold">Appearance</span>
            </div>
            <FiChevronRight 
              size={16}
              style={{
                transform: submenu === "appearance" ? "rotate(90deg)" : "rotate(0deg)",
                transition: "transform 0.2s ease",
              }}
            />
          </button>

          {/* Appearance Submenu */}
          {submenu === "appearance" && (
            <div className="py-2">
              {["Light", "Dark", "System Default"].map((mode) => (
                <button
                  key={mode}
                  onClick={() => {
                    handleModeChange(
                      mode === "Light"
                        ? "light"
                        : mode === "Dark"
                          ? "dark"
                          : "system"
                    );
                    setIsOpen(false);
                  }}
                  className="w-full px-8 py-2 text-sm text-left hover:opacity-80 transition-opacity flex items-center gap-2"
                  style={{
                    color: "var(--text)",
                    backgroundColor:
                      (mode === "Light" && !dark) ||
                      (mode === "Dark" && dark) ||
                      (mode === "System Default" && false)
                        ? "var(--border)"
                        : "transparent",
                    cursor: "pointer",
                  }}
                >
                  {(mode === "Light" && !dark) ||
                  (mode === "Dark" && dark) ||
                  (mode === "System Default" && false) ? (
                    <div style={{ color: "var(--accent)" }}><GoCheck /></div>
                  ) : (
                    <div style={{ width: "16px" }} />
                  )}
                  {mode}
                </button>
              ))}
            </div>
          )}

        </div>
      )}

      {/* Close menu on outside click */}
      {isOpen && (
        <div
          className="fixed inset-0 z-9999"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default SettingsMenu;
