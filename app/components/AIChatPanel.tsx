"use client";

import React, { useCallback, useEffect, useRef, useState } from "react";
import { GoX, GoPaperAirplane } from "react-icons/go";
import { FiMessageSquare } from "react-icons/fi";
import ChatMessageComponent from "./ChatMessage";
import ContextChip from "./ContextChip";
import type { ChatMessage, ContextAttachment, StreamChatEvent } from "../types/ai";

interface AIChatPanelProps {
  isOpen: boolean;
  onClose: () => void;
  contextAttachments: ContextAttachment[];
  onRemoveAttachment: (id: string) => void;
  onClearAttachments: () => void;
  code: string;
  output: string;
  panels: { id: string; kind: string; payload: unknown; varname: string }[];
}

const AIChatPanel: React.FC<AIChatPanelProps> = ({
  isOpen,
  onClose,
  contextAttachments,
  onRemoveAttachment,
  onClearAttachments,
  code,
  output,
  panels,
}) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Focus input when panel opens
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [isOpen]);

  // Send message to AI
  const sendMessage = useCallback(async () => {
    const text = inputValue.trim();
    if (!text || isLoading) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
      role: "user",
      content: text,
      timestamp: Date.now(),
      contextAttachments: contextAttachments.length > 0 ? [...contextAttachments] : undefined,
    };

    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    setInputValue("");
    onClearAttachments();
    setIsLoading(true);

    // Build the messages array for the backend (role + content only)
    const apiMessages = updatedMessages.map((m) => ({
      role: m.role,
      content: m.content,
    }));

    // Prepare structures snapshot for context
    const structures = panels.map((p) => ({
      name: p.varname,
      type: p.kind,
      payload: p.payload,
    }));

    // Create a placeholder assistant message for streaming
    const assistantMsgId = `msg-${Date.now()}-asst`;
    const assistantMsg: ChatMessage = {
      id: assistantMsgId,
      role: "assistant",
      content: "",
      timestamp: Date.now(),
      isStreaming: true,
    };
    setMessages((prev) => [...prev, assistantMsg]);

    try {
      const res = await fetch("/api/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          messages: apiMessages,
          code,
          output,
          structures,
        }),
      });

      console.log("[AI Chat] Response status:", res.status, "ok:", res.ok);

      if (!res.ok) {
        throw new Error("Chat request failed");
      }

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response stream");

      let buffer = "";
      let chunkCount = 0;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        chunkCount++;
        if (chunkCount <= 3) console.log("[AI Chat] chunk", chunkCount, ":", JSON.stringify(chunk).slice(0, 200));
        buffer += chunk;
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.startsWith("data: ")) continue;
          const jsonStr = line.slice(6).trim();
          if (!jsonStr || jsonStr === "[DONE]") continue;

          try {
            const event: StreamChatEvent = JSON.parse(jsonStr);

            if (event.type === "text_delta" && typeof event.delta === "string") {
              const delta = event.delta;
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, content: m.content + delta, runningTool: undefined }
                    : m
                )
              );
            } else if (event.type === "tool_use_start" && event.tool_name) {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, runningTool: event.tool_name }
                    : m
                )
              );
            } else if (event.type === "tool_result") {
              setMessages((prev) =>
                prev.map((m) => {
                  if (m.id !== assistantMsgId) return m;
                  const existingToolCalls = m.toolCalls || [];
                  return {
                    ...m,
                    toolCalls: [
                      ...existingToolCalls,
                      {
                        toolName: event.tool_name || "",
                        toolInput: event.tool_input || {},
                        result: event.result,
                        displayCards: event.display_cards || [],
                      },
                    ],
                    runningTool: undefined,
                  };
                })
              );
            } else if (event.type === "done") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId ? { ...m, isStreaming: false, runningTool: undefined } : m
                )
              );
            } else if (event.type === "error") {
              setMessages((prev) =>
                prev.map((m) =>
                  m.id === assistantMsgId
                    ? { ...m, content: m.content + `\n\n_Error: ${event.error}_`, isStreaming: false, runningTool: undefined }
                    : m
                )
              );
            }
          } catch (parseErr) {
            console.warn("[AI Chat] SSE parse error:", parseErr, "raw:", jsonStr);
          }
        }
      }

      console.log("[AI Chat] Stream finished. Total chunks:", chunkCount);

      // Ensure streaming is finalized
      setMessages((prev) =>
        prev.map((m) => (m.id === assistantMsgId ? { ...m, isStreaming: false, runningTool: undefined } : m))
      );
    } catch (outerErr) {
      console.error("[AI Chat] Outer error:", outerErr);
      setMessages((prev) =>
        prev.map((m) =>
          m.id === assistantMsgId
            ? { ...m, content: "Sorry, I couldn't process your request. Make sure the backend is running.", isStreaming: false, runningTool: undefined }
            : m
        )
      );
    } finally {
      setIsLoading(false);
    }
  }, [inputValue, isLoading, contextAttachments, messages, panels, code, output, onClearAttachments]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="ai-chat-panel"
      style={{
        position: "fixed",
        top: 0,
        right: 0,
        width: "400px",
        height: "100vh",
        display: "flex",
        flexDirection: "column",
        background: "var(--background)",
        borderLeft: "1px solid var(--border)",
        zIndex: 900,
        animation: "slideInRight 0.2s ease-out",
        transition: "background-color 0.3s ease, border-color 0.3s ease",
      }}
    >
      {/* Header */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "14px 16px",
          borderBottom: "1px solid var(--border)",
          background: "var(--subtle-bg)",
          flexShrink: 0,
          transition: "background-color 0.3s ease, border-color 0.3s ease",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <FiMessageSquare size={16} style={{ color: "var(--accent)" }} />
          <span style={{ fontSize: "14px", fontWeight: 600, color: "var(--text)" }}>AI Assistant</span>
        </div>
        <button
          onClick={onClose}
          style={{
            background: "none",
            border: "none",
            color: "var(--panel-text)",
            cursor: "pointer",
            padding: "4px",
            display: "flex",
            alignItems: "center",
            opacity: 0.6,
            transition: "opacity 0.15s ease",
          }}
          onMouseEnter={(e) => { e.currentTarget.style.opacity = "1"; }}
          onMouseLeave={(e) => { e.currentTarget.style.opacity = "0.6"; }}
        >
          <GoX size={18} />
        </button>
      </div>

      {/* Messages area */}
      <div
        className="list-panel-scroll"
        style={{
          flex: 1,
          overflowY: "auto",
          padding: "16px",
          display: "flex",
          flexDirection: "column",
          gap: "8px",
        }}
      >
        {messages.length === 0 && (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              flex: 1,
              gap: "12px",
              opacity: 0.4,
              padding: "40px 20px",
              textAlign: "center",
            }}
          >
            <FiMessageSquare size={32} />
            <div style={{ fontSize: "13px", lineHeight: "1.5" }}>
              Ask me about your code, algorithms, or data structures.
              <br />
              Attach visualizations or code selections for context.
            </div>
          </div>
        )}
        {messages.map((msg) => (
          <ChatMessageComponent key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Context attachments bar */}
      {contextAttachments.length > 0 && (
        <div
          style={{
            display: "flex",
            gap: "6px",
            padding: "8px 16px",
            borderTop: "1px solid var(--border)",
            overflowX: "auto",
            flexShrink: 0,
            background: "var(--subtle-bg)",
            transition: "background-color 0.3s ease, border-color 0.3s ease",
          }}
          className="list-panel-scroll"
        >
          {contextAttachments.map((att) => (
            <ContextChip key={att.id} attachment={att} onRemove={onRemoveAttachment} compact />
          ))}
        </div>
      )}

      {/* Input area */}
      <div
        style={{
          padding: "12px 16px",
          borderTop: "1px solid var(--border)",
          flexShrink: 0,
          background: "var(--subtle-bg)",
          transition: "background-color 0.3s ease, border-color 0.3s ease",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "flex-end",
            gap: "8px",
            background: "var(--panel-content-bg)",
            borderRadius: "10px",
            border: "1px solid var(--border)",
            padding: "8px 12px",
            transition: "border-color 0.2s ease, background-color 0.3s ease",
          }}
        >
          <textarea
            ref={inputRef}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your code..."
            rows={1}
            style={{
              flex: 1,
              border: "none",
              outline: "none",
              resize: "none",
              background: "transparent",
              color: "var(--text)",
              fontSize: "13px",
              fontFamily: "var(--font-inter), var(--font-poppins), sans-serif",
              lineHeight: "1.5",
              maxHeight: "100px",
              overflowY: "auto",
            }}
            onInput={(e) => {
              const target = e.target as HTMLTextAreaElement;
              target.style.height = "auto";
              target.style.height = Math.min(target.scrollHeight, 100) + "px";
            }}
          />
          <button
            onClick={sendMessage}
            disabled={!inputValue.trim() || isLoading}
            style={{
              background: "none",
              border: "none",
              color: inputValue.trim() && !isLoading ? "var(--accent)" : "var(--panel-text)",
              cursor: inputValue.trim() && !isLoading ? "pointer" : "not-allowed",
              opacity: inputValue.trim() && !isLoading ? 1 : 0.3,
              padding: "4px",
              display: "flex",
              alignItems: "center",
              transition: "color 0.15s ease, opacity 0.15s ease",
              flexShrink: 0,
            }}
            aria-label="Send message"
          >
            <GoPaperAirplane size={18} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default AIChatPanel;
