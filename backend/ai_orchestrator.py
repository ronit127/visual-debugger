"""
AI chatbot using Amazon Bedrock Converse API with tool calling.

Yields SSE-style dicts:
  {"type": "text_delta", "delta": "..."}
  {"type": "tool_use", "tool_name": "...", "tool_input": {...}}
  {"type": "tool_result", "tool_name": "...", "result": {...}}
  {"type": "done", "full_text": "..."}
  {"type": "error", "error": "..."}
"""

from __future__ import annotations

import json
import os
import urllib.request
import urllib.parse
from typing import Any, Dict, Generator, List


def search_youtube(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search YouTube for videos and return real links."""
    try:
        # YouTube Data API v3 - free tier, no auth needed for search
        api_key = os.environ.get("YOUTUBE_API_KEY", "")
        if not api_key:
            return {
                "results": [],
                "error": "YOUTUBE_API_KEY not configured. Get one at https://console.cloud.google.com/apis/credentials"
            }

        url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={urllib.parse.quote(query)}&maxResults={max_results}&key={api_key}"

        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())

        results = []
        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            snippet = item.get("snippet", {})
            results.append({
                "type": "youtube",
                "title": snippet.get("title", ""),
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnailUrl": snippet.get("thumbnails", {}).get("medium", {}).get("url", ""),
                "channel": snippet.get("channelTitle", ""),
                "description": snippet.get("description", "")[:80]
            })

        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}


def search_stackoverflow(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search Stack Overflow for questions and return real links."""
    try:
        # Stack Exchange API - free, no auth needed
        url = f"https://api.stackexchange.com/2.3/search/advanced?order=desc&sort=relevance&q={urllib.parse.quote(query)}&site=stackoverflow&pagesize={max_results}"

        req = urllib.request.Request(url)
        req.add_header("Accept-Encoding", "gzip")

        with urllib.request.urlopen(req, timeout=10) as response:
            import gzip
            if response.info().get('Content-Encoding') == 'gzip':
                data = json.loads(gzip.decompress(response.read()).decode())
            else:
                data = json.loads(response.read().decode())

        results = []
        for item in data.get("items", []):
            results.append({
                "type": "stackoverflow",
                "title": item.get("title", ""),
                "url": item.get("link", ""),
                "score": item.get("score", 0),
                "answerCount": item.get("answer_count", 0),
                "isAnswered": item.get("is_answered", False),
                "tags": item.get("tags", [])[:3]
            })

        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}


def search_python_docs(query: str, max_results: int = 5) -> Dict[str, Any]:
    """Search Python documentation and return relevant pages with analysis."""
    try:
        # Use DuckDuckGo to search Python docs
        search_url = f"https://html.duckduckgo.com/html/?q=site:docs.python.org+{urllib.parse.quote(query)}"

        req = urllib.request.Request(search_url)
        req.add_header("User-Agent", "Mozilla/5.0")

        with urllib.request.urlopen(req, timeout=10) as response:
            html_content = response.read().decode()

        # Parse search results - simple HTML parsing
        import re
        results = []

        # Find all result links
        pattern = r'<a class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
        matches = re.findall(pattern, html_content)

        for url, title in matches[:max_results]:
            # Clean up URL (DDG sometimes wraps it)
            if url.startswith("//duckduckgo.com/l/?"):
                # Extract actual URL from DDG redirect
                import urllib.parse as up
                parsed = up.parse_qs(up.urlparse(url).query)
                url = parsed.get('uddg', [url])[0]

            if "docs.python.org" in url:
                # Fetch the actual doc page to get a snippet
                try:
                    doc_req = urllib.request.Request(url)
                    doc_req.add_header("User-Agent", "Mozilla/5.0")
                    with urllib.request.urlopen(doc_req, timeout=5) as doc_response:
                        doc_html = doc_response.read().decode()

                    # Extract first paragraph or relevant text
                    # Simple extraction - get text between <p> tags
                    p_pattern = r'<p[^>]*>([^<]+(?:<[^/p][^>]*>[^<]*</[^>]+>)*[^<]*)</p>'
                    paragraphs = re.findall(p_pattern, doc_html)
                    snippet = ""
                    if paragraphs:
                        # Clean HTML tags from snippet
                        snippet = re.sub(r'<[^>]+>', '', paragraphs[0])[:200]
                except:
                    snippet = "Python documentation page"

                results.append({
                    "type": "python_docs",
                    "title": title.strip(),
                    "url": url,
                    "snippet": snippet
                })

        return {"results": results}
    except Exception as e:
        return {"results": [], "error": str(e)}


def search_session_history(query: str, user_id: str = "default_user", max_results: int = 5) -> Dict[str, Any]:
    """
    Search past debugging sessions for relevant context.
    Allows the AI to learn from previous debugging conversations.
    """
    try:
        from session_store import SessionStore
        store = SessionStore()

        sessions = store.search_sessions(user_id=user_id, query=query, limit=max_results)

        results = []
        for session in sessions:
            # Extract relevant context from the session
            messages = session.get("messages", [])

            # Get a summary of the conversation
            user_messages = [m for m in messages if m.get("role") == "user"]
            ai_messages = [m for m in messages if m.get("role") == "assistant"]

            # Create a summary
            preview = ""
            if user_messages:
                preview = f"User asked: {user_messages[0].get('content', '')[:100]}..."

            results.append({
                "sessionId": session.get("sessionId"),
                "title": session.get("title", ""),
                "preview": preview,
                "messageCount": len(messages),
                "createdAt": session.get("createdAt"),
                "updatedAt": session.get("updatedAt"),
                "relevantMessages": [
                    {
                        "role": m.get("role"),
                        "content": m.get("content", "")[:300]  # Truncate for context
                    }
                    for m in messages[:3]  # First 3 messages for context
                ]
            })

        return {
            "results": results,
            "message": f"Found {len(results)} relevant past debugging sessions"
        }
    except Exception as e:
        return {"results": [], "error": str(e)}


class AIChat:
    """Streaming chat via Bedrock Converse API with tool calling."""

    DEFAULT_MODEL = "us.anthropic.claude-3-5-sonnet-20240620-v1:0"

    SYSTEM_PROMPT = (
        "You are an AI debugging assistant for Visual Debugger, a Python code "
        "visualization tool. Help users understand their code by:\n"
        "1. Explaining what each line does and how data structures change step-by-step\n"
        "2. Identifying bugs and suggesting fixes with corrected code blocks\n"
        "3. Explaining algorithm patterns and time/space complexity\n\n"
        "When users ask for resources, tutorials, or need more information:\n"
        "- Use search_youtube to find video tutorials\n"
        "- Use search_stackoverflow to find relevant Q&A threads\n"
        "- Use search_python_docs to find official Python documentation\n"
        "- Use search_session_history to recall past debugging sessions and learn from them\n\n"
        "Rules:\n"
        "- Use markdown formatting with code blocks\n"
        "- Be concise but thorough\n"
        "- Always show corrected code when fixing bugs\n"
        "- When providing tool results, briefly summarize them\n"
        "- Learn from past sessions to provide better help\n"
    )

    TOOLS = [
        {
            "toolSpec": {
                "name": "search_youtube",
                "description": "Search YouTube for programming tutorials and explanations related to algorithms, data structures, or debugging",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for YouTube videos (e.g. 'binary search tree tutorial', 'graph algorithms explained')"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results to return (default 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "search_stackoverflow",
                "description": "Search Stack Overflow for programming Q&A related to bugs, errors, or implementation questions",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for Stack Overflow (e.g. 'python list index out of range', 'binary tree implementation')"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results to return (default 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "search_python_docs",
                "description": "Search official Python documentation for reference material on built-in functions, modules, or language features",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for Python docs (e.g. 'list comprehension', 'asyncio module', 'dictionary methods')"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results to return (default 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        },
        {
            "toolSpec": {
                "name": "search_session_history",
                "description": "Search past debugging sessions to find relevant context, similar bugs, or previous solutions. Use this to learn from past conversations.",
                "inputSchema": {
                    "json": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Search query for past sessions (e.g. 'binary search bug', 'list indexing error', 'graph traversal')"
                            },
                            "user_id": {
                                "type": "string",
                                "description": "User ID to search sessions for (default 'default_user')",
                                "default": "default_user"
                            },
                            "max_results": {
                                "type": "number",
                                "description": "Maximum number of results to return (default 5)",
                                "default": 5
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        }
    ]

    def __init__(self):
        import boto3

        region = os.environ.get("AWS_REGION", "us-east-1")
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = os.environ.get("BEDROCK_MODEL_ID", self.DEFAULT_MODEL)
        print(f"[AIChat] model={self.model_id} region={region}")

    def _build_system(self, code: str = "", output: str = "", structures: list | None = None) -> str:
        prompt = self.SYSTEM_PROMPT
        if code:
            prompt += f"\n## User's Python Code\n```python\n{code}\n```\n"
        if output:
            prompt += f"\n## Program Output\n```\n{output}\n```\n"
        if structures:
            s = json.dumps(structures, default=str)
            if len(s) > 4000:
                s = s[:4000] + "\n... (truncated)"
            prompt += f"\n## Current Data Structures\n```json\n{s}\n```\n"
        return prompt

    @staticmethod
    def _to_converse_messages(messages: List[Dict[str, Any]]) -> list:
        """Convert {"role", "content"} dicts to Bedrock Converse format."""
        out = []
        for msg in messages:
            role = msg["role"]
            if role == "user":
                text = (msg.get("content") or "").strip() or "..."
                out.append({"role": "user", "content": [{"text": text}]})
            elif role == "assistant":
                # Assistant messages can have text and tool_use blocks
                content_blocks = []
                if msg.get("content"):
                    content_blocks.append({"text": msg["content"]})
                if msg.get("tool_calls"):
                    for tc in msg["tool_calls"]:
                        content_blocks.append({
                            "toolUse": {
                                "toolUseId": tc.get("id", ""),
                                "name": tc.get("name", ""),
                                "input": tc.get("input", {})
                            }
                        })
                if content_blocks:
                    out.append({"role": "assistant", "content": content_blocks})
            elif role == "tool":
                # Tool results go back as user messages with toolResult blocks
                out.append({
                    "role": "user",
                    "content": [{
                        "toolResult": {
                            "toolUseId": msg.get("tool_call_id", ""),
                            "content": [{"json": msg.get("content", {})}]
                        }
                    }]
                })
        return out

    @staticmethod
    def _ensure_alternating(messages: list) -> list:
        """Bedrock requires strictly alternating user/assistant roles."""
        if not messages:
            return messages
        merged: list = [messages[0]]
        for msg in messages[1:]:
            if msg["role"] == merged[-1]["role"]:
                # Merge content blocks
                merged[-1]["content"] = merged[-1]["content"] + msg["content"]
            else:
                merged.append(msg)
        return merged

    def _execute_tool(self, tool_name: str, tool_input: dict) -> dict:
        """Execute a tool and return the result."""
        if tool_name == "search_youtube":
            query = tool_input.get("query", "")
            max_results = int(tool_input.get("max_results", 5))
            return search_youtube(query, max_results)
        elif tool_name == "search_stackoverflow":
            query = tool_input.get("query", "")
            max_results = int(tool_input.get("max_results", 5))
            return search_stackoverflow(query, max_results)
        elif tool_name == "search_python_docs":
            query = tool_input.get("query", "")
            max_results = int(tool_input.get("max_results", 5))
            return search_python_docs(query, max_results)
        elif tool_name == "search_session_history":
            query = tool_input.get("query", "")
            user_id = tool_input.get("user_id", "default_user")
            max_results = int(tool_input.get("max_results", 5))
            return search_session_history(query, user_id, max_results)
        else:
            return {"error": f"Unknown tool: {tool_name}"}

    def stream_chat(
        self,
        messages: List[Dict[str, Any]],
        code: str = "",
        output: str = "",
        structures: list | None = None,
        max_turns: int = 5,
    ) -> Generator[Dict[str, Any], None, None]:
        """Stream a chat conversation with tool calling support."""
        system = self._build_system(code, output, structures)
        conversation = messages.copy()

        for turn in range(max_turns):
            converse_messages = self._to_converse_messages(conversation)
            converse_messages = self._ensure_alternating(converse_messages)

            try:
                response = self.client.converse_stream(
                    modelId=self.model_id,
                    system=[{"text": system}],
                    messages=converse_messages,
                    toolConfig={"tools": self.TOOLS},
                    inferenceConfig={"maxTokens": 4096, "temperature": 0.7},
                )
            except Exception as exc:
                yield {"type": "error", "error": f"Bedrock error: {exc}"}
                return

            full_text = ""
            tool_uses = []
            stop_reason = None

            try:
                for event_wrapper in response.get("stream", []):
                    if "contentBlockStart" in event_wrapper:
                        start = event_wrapper["contentBlockStart"]["start"]
                        if "toolUse" in start:
                            tool_use = start["toolUse"]
                            tool_uses.append({
                                "id": tool_use.get("toolUseId", ""),
                                "name": tool_use.get("name", ""),
                                "input": ""
                            })
                            yield {
                                "type": "tool_use_start",
                                "tool_name": tool_use.get("name", "")
                            }

                    elif "contentBlockDelta" in event_wrapper:
                        delta = event_wrapper["contentBlockDelta"]["delta"]
                        if "text" in delta:
                            text = delta["text"]
                            full_text += text
                            yield {"type": "text_delta", "delta": text}
                        elif "toolUse" in delta:
                            # Accumulate tool input JSON
                            if tool_uses:
                                tool_uses[-1]["input"] += delta["toolUse"].get("input", "")

                    elif "messageStop" in event_wrapper:
                        stop_reason = event_wrapper["messageStop"].get("stopReason")

                    elif "internalServerException" in event_wrapper or "modelStreamErrorException" in event_wrapper:
                        err = event_wrapper.get(
                            "internalServerException",
                            event_wrapper.get("modelStreamErrorException", {}),
                        )
                        yield {"type": "error", "error": f"Bedrock stream error: {err}"}
                        return
            except Exception as stream_exc:
                yield {"type": "error", "error": f"Stream error: {type(stream_exc).__name__}: {stream_exc}"}
                return

            # Add assistant message to conversation
            assistant_msg = {"role": "assistant", "content": full_text}
            if tool_uses:
                # Parse tool input JSON
                for tu in tool_uses:
                    try:
                        tu["input"] = json.loads(tu["input"]) if tu["input"] else {}
                    except:
                        tu["input"] = {}
                assistant_msg["tool_calls"] = tool_uses
            conversation.append(assistant_msg)

            # If we need to execute tools, do it
            if stop_reason == "tool_use" and tool_uses:
                for tool_use in tool_uses:
                    tool_name = tool_use["name"]
                    tool_input = tool_use["input"]

                    # Execute tool
                    result = self._execute_tool(tool_name, tool_input)

                    # Yield tool result event with display cards
                    display_cards = result.get("results", [])
                    yield {
                        "type": "tool_result",
                        "tool_name": tool_name,
                        "tool_input": tool_input,
                        "result": result,
                        "display_cards": display_cards
                    }

                    # Add tool result to conversation
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_use["id"],
                        "content": result
                    })

                # Continue to next turn to get model's response to tool results
                continue
            else:
                # No more tools to use, we're done
                break

        yield {"type": "done", "full_text": full_text}
