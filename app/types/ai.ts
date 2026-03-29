// ── Context Attachments ──────────────────────────────────────────

export interface ContextAttachment {
  id: string;
  type: "visualization" | "code_selection" | "terminal_output";
  label: string;
  preview: string;
  fullData: Record<string, unknown>;
  panelKind?: string;
  timestamp: number;
}

// ── Chat Messages ────────────────────────────────────────────────

export interface ToolCall {
  toolName: string;
  toolInput: Record<string, unknown>;
  result?: Record<string, unknown>;
  displayCards?: ResourceCard[];
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: number;
  contextAttachments?: ContextAttachment[];
  toolCalls?: ToolCall[];
  isStreaming?: boolean;
  runningTool?: string;
}

// ── SSE Stream Events ────────────────────────────────────────────

export interface StreamChatEvent {
  type: "text_delta" | "tool_use_start" | "tool_result" | "done" | "error";
  delta?: string;
  tool_name?: string;
  tool_input?: Record<string, unknown>;
  result?: Record<string, unknown>;
  display_cards?: ResourceCard[];
  fullText?: string;
  error?: string;
}

// ── Resource Cards ──────────────────────────────────────────────

export type ResourceCard = YouTubeCard | StackOverflowCard | PythonDocsCard;

export interface YouTubeCard {
  type: "youtube";
  title: string;
  url: string;
  thumbnailUrl: string;
  channel: string;
  description: string;
}

export interface StackOverflowCard {
  type: "stackoverflow";
  title: string;
  url: string;
  score: number;
  answerCount: number;
  isAnswered: boolean;
  tags: string[];
}

export interface PythonDocsCard {
  type: "python_docs";
  title: string;
  url: string;
  snippet: string;
}
