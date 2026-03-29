"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import ContextChip from "./ContextChip";
import ResourceCard from "./ResourceCard";
import type { ChatMessage as ChatMessageType } from "../types/ai";

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessageComponent: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: isUser ? "flex-end" : "flex-start",
        gap: "6px",
        padding: "4px 0",
      }}
    >
      {/* Context attachments on user messages */}
      {isUser && message.contextAttachments && message.contextAttachments.length > 0 && (
        <div style={{ display: "flex", flexWrap: "wrap", gap: "4px", maxWidth: "85%" }}>
          {message.contextAttachments.map((att) => (
            <ContextChip key={att.id} attachment={att} compact />
          ))}
        </div>
      )}

      {/* Message bubble */}
      <div
        style={{
          maxWidth: "85%",
          padding: "10px 14px",
          borderRadius: isUser ? "14px 14px 4px 14px" : "14px 14px 14px 4px",
          background: isUser ? "var(--accent)" : "var(--segment-bg)",
          color: isUser ? "#ffffff" : "var(--text)",
          fontSize: "13px",
          lineHeight: "1.5",
          transition: "background-color 0.2s ease, color 0.2s ease",
          wordBreak: "break-word",
        }}
      >
        {isUser ? (
          <span>{message.content}</span>
        ) : (
          <div className="chat-markdown">
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={{
                code: ({ children, className, ...props }) => {
                  const isInline = !className;
                  if (isInline) {
                    return (
                      <code
                        style={{
                          background: "var(--subtle-bg)",
                          padding: "1px 5px",
                          borderRadius: "4px",
                          fontSize: "12px",
                          fontFamily: "var(--font-jetbrains-mono), monospace",
                        }}
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  }
                  return (
                    <code
                      className={className}
                      style={{
                        display: "block",
                        background: "var(--background)",
                        padding: "10px 12px",
                        borderRadius: "6px",
                        fontSize: "12px",
                        fontFamily: "var(--font-jetbrains-mono), monospace",
                        overflowX: "auto",
                        margin: "6px 0",
                        border: "1px solid var(--border)",
                      }}
                      {...props}
                    >
                      {children}
                    </code>
                  );
                },
                pre: ({ children }) => <>{children}</>,
                p: ({ children }) => <p style={{ margin: "4px 0" }}>{children}</p>,
                ul: ({ children }) => <ul style={{ margin: "4px 0", paddingLeft: "18px" }}>{children}</ul>,
                ol: ({ children }) => <ol style={{ margin: "4px 0", paddingLeft: "18px" }}>{children}</ol>,
                li: ({ children }) => <li style={{ margin: "2px 0" }}>{children}</li>,
                h1: ({ children }) => <h1 style={{ fontSize: "16px", fontWeight: 700, margin: "8px 0 4px" }}>{children}</h1>,
                h2: ({ children }) => <h2 style={{ fontSize: "15px", fontWeight: 600, margin: "8px 0 4px" }}>{children}</h2>,
                h3: ({ children }) => <h3 style={{ fontSize: "14px", fontWeight: 600, margin: "6px 0 2px" }}>{children}</h3>,
              }}
            >
              {message.content}
            </ReactMarkdown>
          </div>
        )}
      </div>

      {/* Streaming / tool-running indicator */}
      {message.isStreaming && (
        <div style={{ display: "flex", flexDirection: "column", gap: "4px", paddingLeft: "8px" }}>
          {message.runningTool ? (
            <div
              style={{
                fontSize: "11px",
                color: "var(--accent)",
                fontStyle: "italic",
                opacity: 0.8,
                display: "flex",
                alignItems: "center",
                gap: "6px",
              }}
            >
              <span style={{ display: "flex", gap: "2px" }}>
                <span className="streaming-dot" style={{ animationDelay: "0s" }} />
                <span className="streaming-dot" style={{ animationDelay: "0.15s" }} />
                <span className="streaming-dot" style={{ animationDelay: "0.3s" }} />
              </span>
              Running {message.runningTool.replace(/_/g, " ")}…
            </div>
          ) : (
            <div style={{ display: "flex", gap: "3px" }}>
              <span className="streaming-dot" style={{ animationDelay: "0s" }} />
              <span className="streaming-dot" style={{ animationDelay: "0.15s" }} />
              <span className="streaming-dot" style={{ animationDelay: "0.3s" }} />
            </div>
          )}
        </div>
      )}

      {/* Tool call results - Resource cards */}
      {message.toolCalls && message.toolCalls.length > 0 && (
        <div
          style={{
            display: "flex",
            gap: "8px",
            overflowX: "auto",
            paddingBottom: "4px",
            maxWidth: "100%",
          }}
          className="list-panel-scroll"
        >
          {message.toolCalls.flatMap((tc) =>
            (tc.displayCards || []).map((card, i) => (
              <ResourceCard key={`${tc.toolName}-${i}`} resource={card} />
            ))
          )}
        </div>
      )}
    </div>
  );
};

export default ChatMessageComponent;
