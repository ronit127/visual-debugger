"use client";

import React, { useState, useEffect } from "react";
import { FiPlus, FiTrash2, FiMessageSquare } from "react-icons/fi";

interface Session {
  sessionId: string;
  title: string;
  createdAt: number;
  updatedAt: number;
  messageCount?: number;
}

interface SessionSidebarProps {
  currentSessionId: string | null;
  onSessionSelect: (sessionId: string) => void;
  onNewSession: () => void;
}

const SessionSidebar: React.FC<SessionSidebarProps> = ({
  currentSessionId,
  onSessionSelect,
  onNewSession,
}) => {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const loadSessions = async () => {
    try {
      const res = await fetch("/api/ai/sessions?userId=default_user");
      if (res.ok) {
        const data = await res.json();
        setSessions(data.sessions || []);
      }
    } catch (error) {
      console.error("Failed to load sessions:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleDelete = async (sessionId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (!confirm("Delete this session?")) return;

    try {
      const res = await fetch(`/api/ai/sessions/${sessionId}`, {
        method: "DELETE",
      });
      if (res.ok) {
        setSessions((prev) => prev.filter((s) => s.sessionId !== sessionId));
        if (currentSessionId === sessionId) {
          onNewSession();
        }
      }
    } catch (error) {
      console.error("Failed to delete session:", error);
    }
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffMins < 1440) return `${Math.floor(diffMins / 60)}h ago`;
    return date.toLocaleDateString();
  };

  return (
    <div
      style={{
        width: "280px",
        height: "100%",
        background: "var(--panel-bg)",
        borderRight: "1px solid var(--border)",
        display: "flex",
        flexDirection: "column",
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: "16px",
          borderBottom: "1px solid var(--border)",
        }}
      >
        <button
          onClick={onNewSession}
          style={{
            width: "100%",
            padding: "10px",
            background: "var(--accent)",
            color: "white",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            fontWeight: 600,
            fontSize: "14px",
          }}
        >
          <FiPlus size={16} />
          New Session
        </button>
      </div>

      {/* Sessions List */}
      <div
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "8px",
        }}
      >
        {isLoading ? (
          <div style={{ padding: "20px", textAlign: "center", color: "var(--panel-text)" }}>
            Loading...
          </div>
        ) : sessions.length === 0 ? (
          <div
            style={{
              padding: "20px",
              textAlign: "center",
              color: "var(--panel-text)",
              opacity: 0.6,
            }}
          >
            No sessions yet
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.sessionId}
              onClick={() => onSessionSelect(session.sessionId)}
              style={{
                padding: "12px",
                marginBottom: "4px",
                borderRadius: "6px",
                cursor: "pointer",
                background:
                  currentSessionId === session.sessionId
                    ? "var(--accent-bg)"
                    : "transparent",
                border:
                  currentSessionId === session.sessionId
                    ? "1px solid var(--accent)"
                    : "1px solid transparent",
                transition: "all 0.15s ease",
              }}
              onMouseEnter={(e) => {
                if (currentSessionId !== session.sessionId) {
                  e.currentTarget.style.background = "var(--subtle-bg)";
                }
              }}
              onMouseLeave={(e) => {
                if (currentSessionId !== session.sessionId) {
                  e.currentTarget.style.background = "transparent";
                }
              }}
            >
              <div style={{ display: "flex", alignItems: "flex-start", gap: "8px" }}>
                <FiMessageSquare
                  size={16}
                  style={{ color: "var(--panel-text)", marginTop: "2px", flexShrink: 0 }}
                />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div
                    style={{
                      fontSize: "13px",
                      fontWeight: 600,
                      color: "var(--text)",
                      marginBottom: "4px",
                      overflow: "hidden",
                      textOverflow: "ellipsis",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {session.title}
                  </div>
                  <div
                    style={{
                      fontSize: "11px",
                      color: "var(--panel-text)",
                      opacity: 0.7,
                    }}
                  >
                    {formatDate(session.updatedAt)}
                    {session.messageCount !== undefined && ` • ${session.messageCount} msgs`}
                  </div>
                </div>
                <button
                  onClick={(e) => handleDelete(session.sessionId, e)}
                  style={{
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    padding: "4px",
                    color: "var(--panel-text)",
                    opacity: 0.6,
                    transition: "opacity 0.15s ease",
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.opacity = "1";
                    e.currentTarget.style.color = "#ef4444";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.opacity = "0.6";
                    e.currentTarget.style.color = "var(--panel-text)";
                  }}
                >
                  <FiTrash2 size={14} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SessionSidebar;