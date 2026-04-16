from __future__ import annotations

import contextlib
import io
import json
import os
import sys
import time
import traceback
from collections import deque
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

# ── Load .env file (simple parser, no dotenv package needed) ──────
_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_ENV_PATH):
    with open(_ENV_PATH) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _, _v = _line.partition("=")
                _k = _k.strip()
                _v = _v.strip()
                if _k and _k not in os.environ:   # don't override real env vars
                    os.environ[_k] = _v

app = Flask(__name__)
CORS(app)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _safe_serialize(obj: Any, *, max_depth: int = 4, max_items: int = 80) -> Any:
    def inner(o: Any, depth: int) -> Any:
        if depth <= 0:
            return "<max_depth>"

        if o is None or isinstance(o, (bool, int, float, str)):
            return o

        if isinstance(o, (bytes, bytearray, memoryview)):
            return f"<{type(o).__name__} {len(o)} bytes>"

        if isinstance(o, (list, tuple, deque)):
            out: List[Any] = []
            for i, item in enumerate(o):
                if i >= max_items:
                    out.append(f"<+{len(o) - max_items} more>")
                    break
                out.append(inner(item, depth - 1))
            return out if isinstance(o, (list, deque)) else tuple(out)

        if isinstance(o, set):
            items = list(o)
            items.sort(key=lambda x: str(type(x)) + ":" + repr(x))
            return [inner(x, depth - 1) for x in items[:max_items]]

        if isinstance(o, dict):
            out: Dict[str, Any] = {}
            for i, (k, v) in enumerate(list(o.items())):
                if i >= max_items:
                    out["<truncated>"] = f"<+{len(o) - max_items} more>"
                    break
                out[str(inner(k, depth - 1))] = inner(v, depth - 1)
            return out

        if isinstance(o, Graph):
            return {
                "nodes": list(o.nodes.values()),
                "links": list(o.links),
            }

        if isinstance(o, Heap):
            return list(o.data)

        return repr(o)

    return inner(obj, max_depth)


def _infer_list_op(before: Any, after: Any) -> str:
    if not isinstance(before, list) or not isinstance(after, list):
        return "mutate"
    if len(after) == len(before) + 1 and after[: len(before)] == before:
        return "append"
    if len(after) == len(before) - 1 and before[: len(after)] == after:
        return "pop"
    if len(after) >= len(before) and all(x in after for x in before):
        return "extend"
    return "mutate"


def _infer_dict_op(before: Any, after: Any) -> str:
    if not isinstance(before, dict) or not isinstance(after, dict):
        return "mutate"
    before_keys = set(before.keys())
    after_keys = set(after.keys())
    if after_keys - before_keys:
        return "set"
    if before_keys - after_keys:
        return "del"
    for k in after_keys:
        if before.get(k) != after.get(k):
            return "set"
    return "mutate"


def _find_names_for_object(frame, obj_id: int) -> List[str]:
    names: List[str] = []
    try:
        for scope in (frame.f_locals, frame.f_globals):
            for k, v in scope.items():
                if isinstance(k, str) and id(v) == obj_id:
                    names.append(k)
    except Exception:
        return names
    # de-dupe while preserving order
    seen = set()
    out: List[str] = []
    for n in names:
        if n not in seen:
            seen.add(n)
            out.append(n)
    return out


@dataclass
class TimelineEvent:
    step: int
    ts_ms: int
    event: str
    line: Optional[int] = None
    func: Optional[str] = None
    var: Optional[str] = None
    object_id: Optional[int] = None
    op: Optional[str] = None
    before: Any = None
    after: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "ts_ms": self.ts_ms,
            "event": self.event,
            "line": self.line,
            "func": self.func,
            "var": self.var,
            "object_id": self.object_id,
            "op": self.op,
            "before": self.before,
            "after": self.after,
        }


class TimelineRecorder:
    def __init__(self, *, max_steps: int = 50000) -> None:
        self.events: List[TimelineEvent] = []
        # A full snapshot of all tracked structures for each emitted step.
        # This makes frontend scrubbing simple and accurate.
        self.states: List[Dict[str, Any]] = []
        self._step = 0
        self._last_snapshot_by_id: Dict[int, Any] = {}
        self._max_steps = max_steps

    def _snapshot_structures(self, frame) -> List[Dict[str, Any]]:
        merged: Dict[str, Any] = {}
        try:
            # globals first, locals override
            for scope in (frame.f_globals, frame.f_locals):
                for k, v in scope.items():
                    if not isinstance(k, str):
                        continue
                    if k.startswith("__"):
                        continue
                    if isinstance(v, (list, dict, Heap, Graph)):
                        merged[k] = v
        except Exception:
            return []

        out: List[Dict[str, Any]] = []
        for name, value in merged.items():
            try:
                if isinstance(value, Graph):
                    kind = "graph"
                elif isinstance(value, Heap):
                    kind = "heap"
                elif isinstance(value, dict):
                    kind = "dict"
                else:
                    kind = "list"
                out.append(
                    {
                        "name": name,
                        "type": kind,
                        "object_id": id(value),
                        "payload": _safe_serialize(value),
                    }
                )
            except Exception:
                continue

        # stable ordering for UI
        out.sort(key=lambda s: (s.get("type", ""), s.get("name", "")))
        return out

    def emit(
        self,
        *,
        event: str,
        line: Optional[int] = None,
        func: Optional[str] = None,
        var: Optional[str] = None,
        object_id: Optional[int] = None,
        op: Optional[str] = None,
        before: Any = None,
        after: Any = None,
        frame=None,
    ) -> None:
        if self._step >= self._max_steps:
            raise RuntimeError(f"Max steps exceeded ({self._max_steps}).")
        self._step += 1
        self.events.append(
            TimelineEvent(
                step=self._step,
                ts_ms=_now_ms(),
                event=event,
                line=line,
                func=func,
                var=var,
                object_id=object_id,
                op=op,
                before=before,
                after=after,
            )
        )

        # Also store a full snapshot for this step.
        state_structures: List[Dict[str, Any]] = []
        if frame is not None:
            state_structures = self._snapshot_structures(frame)
        self.states.append(
            {
                "step": self._step,
                "line": line,
                "func": func,
                "event": event,
                "structures": state_structures,
            }
        )

    def snapshot_watchables(self, frame, *, line: Optional[int] = None) -> None:
        # Compare local/global objects to detect mutations in watchable containers.
        # This powers timeline replay without re-executing code.
        watch: Dict[int, Tuple[str, Any]] = {}
        try:
            for scope in (frame.f_globals, frame.f_locals):
                for k, v in scope.items():
                    if not isinstance(k, str):
                        continue
                    if k.startswith("__"):
                        continue
                    if isinstance(v, (list, dict, Heap, Graph)):
                        watch[id(v)] = (k, v)
        except Exception:
            return

        event_line = line if line is not None else getattr(frame, "f_lineno", None)
        event_func = getattr(frame.f_code, "co_name", None)

        for obj_id, (name, obj) in watch.items():
            current = _safe_serialize(obj)
            prev = self._last_snapshot_by_id.get(obj_id)
            if prev is None:
                # Emit an init event so the frontend can render the initial state.
                self.emit(
                    event="mutation",
                    line=event_line,
                    func=event_func,
                    var=name,
                    object_id=obj_id,
                    op="init",
                    before=None,
                    after=current,
                    frame=frame,
                )
                self._last_snapshot_by_id[obj_id] = current
                continue
            if prev != current:
                op = "mutate"
                if isinstance(obj, list):
                    op = _infer_list_op(prev, current)
                elif isinstance(obj, dict):
                    op = _infer_dict_op(prev, current)
                self.emit(
                    event="mutation",
                    line=event_line,
                    func=event_func,
                    var=name,
                    object_id=obj_id,
                    op=op,
                    before=prev,
                    after=current,
                    frame=frame,
                )
                self._last_snapshot_by_id[obj_id] = current


class LoggedList(list):
    def __init__(self, iterable=(), *, _recorder: Optional[TimelineRecorder] = None) -> None:
        super().__init__(iterable)
        self._recorder = _recorder

    def _log(self, frame, op: str, before: Any, after: Any) -> None:
        if not self._recorder:
            return
        obj_id = id(self)
        names = _find_names_for_object(frame, obj_id) if frame else []
        self._recorder.emit(
            event="mutation",
            line=getattr(frame, "f_lineno", None) if frame else None,
            func=getattr(frame.f_code, "co_name", None) if frame else None,
            var=(names[0] if names else None),
            object_id=obj_id,
            op=op,
            before=before,
            after=after,
            frame=frame,
        )

    def append(self, x) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().append(x)
        after = _safe_serialize(list(self))
        self._log(frame, "append", before, after)

    def extend(self, it) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().extend(it)
        after = _safe_serialize(list(self))
        self._log(frame, "extend", before, after)

    def insert(self, i, x) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().insert(i, x)
        after = _safe_serialize(list(self))
        self._log(frame, "insert", before, after)

    def pop(self, i: int = -1):
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        out = super().pop(i)
        after = _safe_serialize(list(self))
        self._log(frame, "pop", before, after)
        return out

    def remove(self, x) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().remove(x)
        after = _safe_serialize(list(self))
        self._log(frame, "remove", before, after)

    def clear(self) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().clear()
        after = _safe_serialize(list(self))
        self._log(frame, "clear", before, after)

    def __setitem__(self, key, value) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().__setitem__(key, value)
        after = _safe_serialize(list(self))
        self._log(frame, "setitem", before, after)

    def __delitem__(self, key) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(list(self))
        super().__delitem__(key)
        after = _safe_serialize(list(self))
        self._log(frame, "delitem", before, after)


class LoggedDict(dict):
    def __init__(self, *args, _recorder: Optional[TimelineRecorder] = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._recorder = _recorder

    def _log(self, frame, op: str, before: Any, after: Any) -> None:
        if not self._recorder:
            return
        obj_id = id(self)
        names = _find_names_for_object(frame, obj_id) if frame else []
        self._recorder.emit(
            event="mutation",
            line=getattr(frame, "f_lineno", None) if frame else None,
            func=getattr(frame.f_code, "co_name", None) if frame else None,
            var=(names[0] if names else None),
            object_id=obj_id,
            op=op,
            before=before,
            after=after,
            frame=frame,
        )

    def __setitem__(self, key, value) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        super().__setitem__(key, value)
        after = _safe_serialize(dict(self))
        self._log(frame, "set", before, after)

    def __delitem__(self, key) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        super().__delitem__(key)
        after = _safe_serialize(dict(self))
        self._log(frame, "del", before, after)

    def pop(self, key, default=None):
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        out = super().pop(key, default)
        after = _safe_serialize(dict(self))
        self._log(frame, "pop", before, after)
        return out

    def popitem(self):
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        out = super().popitem()
        after = _safe_serialize(dict(self))
        self._log(frame, "popitem", before, after)
        return out

    def clear(self) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        super().clear()
        after = _safe_serialize(dict(self))
        self._log(frame, "clear", before, after)

    def update(self, *args, **kwargs) -> None:
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        super().update(*args, **kwargs)
        after = _safe_serialize(dict(self))
        self._log(frame, "update", before, after)

    def setdefault(self, key, default=None):
        frame = sys._getframe(1)
        before = _safe_serialize(dict(self))
        out = super().setdefault(key, default)
        after = _safe_serialize(dict(self))
        if before != after:
            self._log(frame, "setdefault", before, after)
        return out


class Heap:
    def __init__(self, iterable=(), *, _recorder: Optional[TimelineRecorder] = None) -> None:
        import heapq

        self.data = list(iterable)
        self._recorder = _recorder
        heapq.heapify(self.data)

    def _log(self, frame, op: str, before: Any, after: Any) -> None:
        if not self._recorder:
            return
        obj_id = id(self)
        names = _find_names_for_object(frame, obj_id) if frame else []
        self._recorder.emit(
            event="mutation",
            line=getattr(frame, "f_lineno", None) if frame else None,
            func=getattr(frame.f_code, "co_name", None) if frame else None,
            var=(names[0] if names else None),
            object_id=obj_id,
            op=op,
            before=before,
            after=after,
            frame=frame,
        )

    def heappush(self, x) -> None:
        import heapq

        frame = sys._getframe(1)
        before = _safe_serialize(list(self.data))
        heapq.heappush(self.data, x)
        after = _safe_serialize(list(self.data))
        self._log(frame, "heappush", before, after)

    def heappop(self):
        import heapq

        frame = sys._getframe(1)
        before = _safe_serialize(list(self.data))
        out = heapq.heappop(self.data)
        after = _safe_serialize(list(self.data))
        self._log(frame, "heappop", before, after)
        return out

    def heapify(self) -> None:
        import heapq

        frame = sys._getframe(1)
        before = _safe_serialize(list(self.data))
        heapq.heapify(self.data)
        after = _safe_serialize(list(self.data))
        self._log(frame, "heapify", before, after)

    def heapreplace(self, x):
        import heapq

        frame = sys._getframe(1)
        before = _safe_serialize(list(self.data))
        out = heapq.heapreplace(self.data, x)
        after = _safe_serialize(list(self.data))
        self._log(frame, "heapreplace", before, after)
        return out

    def heappushpop(self, x):
        import heapq

        frame = sys._getframe(1)
        before = _safe_serialize(list(self.data))
        out = heapq.heappushpop(self.data, x)
        after = _safe_serialize(list(self.data))
        self._log(frame, "heappushpop", before, after)
        return out


class Graph:
    def __init__(self, *, _recorder: Optional[TimelineRecorder] = None) -> None:
        self.nodes: Dict[int, Dict[str, Any]] = {}
        self.links: List[Dict[str, int]] = []
        self._next_id = 1
        self._node_key_to_id: Dict[Any, int] = {}
        self._recorder = _recorder

    def _resolve_node_id(self, value: Any, *, create: bool) -> Optional[int]:
        # Prefer numeric IDs when possible.
        if isinstance(value, (int, float)):
            try:
                node_id = int(value)
                # Treat floats like 1.0 as 1, but keep label as original.
                return node_id
            except Exception:
                pass

        if value in self._node_key_to_id:
            return self._node_key_to_id[value]
        if not create:
            return None
        node_id = self._next_id
        self._next_id += 1
        self._node_key_to_id[value] = node_id
        return node_id

    def _ensure_node(self, value: Any) -> int:
        node_id = self._resolve_node_id(value, create=True)
        assert node_id is not None
        if node_id not in self.nodes:
            self.nodes[node_id] = {"id": node_id, "label": str(value)}
        return node_id

    def _log(self, frame, op: str, before: Any, after: Any) -> None:
        if not self._recorder:
            return
        obj_id = id(self)
        names = _find_names_for_object(frame, obj_id) if frame else []
        self._recorder.emit(
            event="mutation",
            line=getattr(frame, "f_lineno", None) if frame else None,
            func=getattr(frame.f_code, "co_name", None) if frame else None,
            var=(names[0] if names else None),
            object_id=obj_id,
            op=op,
            before=before,
            after=after,
            frame=frame,
        )

    def _snapshot(self) -> Any:
        return _safe_serialize({"nodes": list(self.nodes.values()), "links": list(self.links)})

    def add_node(self, value: Any = None, *args, **kwargs) -> int:
        frame = sys._getframe(1)
        before = self._snapshot()
        node_id = self._ensure_node(value)
        after = self._snapshot()
        self._log(frame, "add_node", before, after)
        return node_id

    def add_edge(self, src: Any, tgt: Any, *args, **kwargs) -> None:
        frame = sys._getframe(1)
        before = self._snapshot()
        s = self._ensure_node(src)
        t = self._ensure_node(tgt)
        self.links.append({"source": s, "target": t})
        after = self._snapshot()
        self._log(frame, "add_edge", before, after)

    def add_nodes_from(self, nodes, *args, **kwargs) -> None:
        for n in list(nodes):
            self.add_node(n)

    def add_edges_from(self, edges, *args, **kwargs) -> None:
        for e in list(edges):
            if isinstance(e, (tuple, list)) and len(e) >= 2:
                self.add_edge(e[0], e[1])

    def remove_node(self, node: Any, *args, **kwargs) -> None:
        frame = sys._getframe(1)
        before = self._snapshot()
        n = self._resolve_node_id(node, create=False)
        if n is not None:
            self.nodes.pop(n, None)
            self.links[:] = [l for l in self.links if l["source"] != n and l["target"] != n]
        after = self._snapshot()
        self._log(frame, "remove_node", before, after)

    def remove_nodes_from(self, nodes, *args, **kwargs) -> None:
        for n in list(nodes):
            try:
                self.remove_node(n)
            except Exception:
                continue

    def remove_edge(self, src: Any, tgt: Any, *args, **kwargs) -> None:
        frame = sys._getframe(1)
        before = self._snapshot()
        s = self._resolve_node_id(src, create=False)
        t = self._resolve_node_id(tgt, create=False)
        if s is not None and t is not None:
            self.links[:] = [l for l in self.links if not (l["source"] == s and l["target"] == t)]
        after = self._snapshot()
        self._log(frame, "remove_edge", before, after)

    def remove_edges_from(self, edges, *args, **kwargs) -> None:
        for e in list(edges):
            if isinstance(e, (tuple, list)) and len(e) >= 2:
                try:
                    self.remove_edge(e[0], e[1])
                except Exception:
                    continue

    def neighbors(self, node: Any) -> List[Any]:
        """Return neighbors of a given node."""
        node_id = self._resolve_node_id(node, create=False)
        if node_id is None:
            return []
        neighbors = []
        for link in self.links:
            if link["source"] == node_id:
                for nid, node_data in self.nodes.items():
                    if nid == link["target"]:
                        neighbors.append(self._node_id_to_value(nid))
            elif link["target"] == node_id:
                for nid, node_data in self.nodes.items():
                    if nid == link["source"]:
                        neighbors.append(self._node_id_to_value(nid))
        return neighbors

    def _node_id_to_value(self, node_id: int) -> Any:
        """Convert a node ID back to its original value."""
        for value, nid in self._node_key_to_id.items():
            if nid == node_id:
                return value
        # For numeric nodes, return the ID itself
        return node_id


class _NetworkXShim:
    """Minimal networkx-like shim so user code `import networkx as nx` works.

    This is intentionally not full NetworkX.
    Supported: Graph/DiGraph/MultiGraph/MultiDiGraph constructors.
    """

    def __init__(self, recorder: TimelineRecorder) -> None:
        self._recorder = recorder

        def graph_factory(*args, **kwargs):
            return Graph(_recorder=self._recorder)

        self.Graph = graph_factory
        self.DiGraph = graph_factory
        self.MultiGraph = graph_factory
        self.MultiDiGraph = graph_factory

    def __getattr__(self, name: str):
        raise AttributeError(
            f"networkx shim only supports Graph/DiGraph/MultiGraph/MultiDiGraph; missing '{name}'"
        )


def _make_safe_builtins(
    allowed_imports: Optional[set[str]] = None,
    *,
    import_overrides: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    if allowed_imports is None:
        allowed_imports = {"math", "heapq", "networkx"}

    def limited_import(name, globals=None, locals=None, fromlist=(), level=0):
        if import_overrides and name in import_overrides:
            return import_overrides[name]
        root = name.split(".", 1)[0]
        if root not in allowed_imports:
            raise ImportError(f"import of '{root}' is disabled")
        return __import__(name, globals, locals, fromlist, level)

    # Intentionally small set; add more as needed.
    safe: Dict[str, Any] = {
        "__import__": limited_import,
        "print": print,
        "range": range,
        "len": len,
        "enumerate": enumerate,
        "int": int,
        "float": float,
        "str": str,
        "bool": bool,
        "list": list,
        "dict": dict,
        "set": set,
        "tuple": tuple,
        "min": min,
        "max": max,
        "sum": sum,
        "abs": abs,
        "all": all,
        "any": any,
        "zip": zip,
        "sorted": sorted,
        "reversed": reversed,
        "Exception": Exception,
        "ValueError": ValueError,
        "TypeError": TypeError,
    }
    return safe


def _trace_factory(recorder: TimelineRecorder, *, filename: str):
    last_executed_line_by_frame: Dict[int, Optional[int]] = {}

    def tracer(frame, event: str, arg):
        if frame.f_code.co_filename != filename:
            return tracer

        if event == "call":
            last_executed_line_by_frame[id(frame)] = None
            recorder.emit(event="call", line=frame.f_lineno, func=frame.f_code.co_name, frame=frame)
        elif event == "line":
            # NOTE: CPython fires 'line' events *before* executing the line.
            # That means the current frame state reflects effects of the *previous executed* line.
            # We attribute container init/mutations to that previous executed line so blank lines
            # don't shift events down (e.g. arr2 init showing at line 5).
            prev_line = last_executed_line_by_frame.get(id(frame))
            recorder.snapshot_watchables(frame, line=prev_line)
            recorder.emit(event="line", line=frame.f_lineno, func=frame.f_code.co_name, frame=frame)
            last_executed_line_by_frame[id(frame)] = frame.f_lineno
        elif event == "return":
            # Snapshot once more at function/module exit so assignments on the last
            # executed line (no next 'line' event) still produce init/mutation events.
            prev_line = last_executed_line_by_frame.get(id(frame), frame.f_lineno)
            recorder.snapshot_watchables(frame, line=prev_line)
            recorder.emit(event="return", line=frame.f_lineno, func=frame.f_code.co_name, frame=frame)
            last_executed_line_by_frame.pop(id(frame), None)
        elif event == "exception":
            # Same idea as 'return': capture final state even when aborting.
            prev_line = last_executed_line_by_frame.get(id(frame), getattr(frame, "f_lineno", None))
            recorder.snapshot_watchables(frame, line=prev_line)
        return tracer

    return tracer


def _collect_structures(final_globals: Dict[str, Any]) -> List[Dict[str, Any]]:
    structures: List[Dict[str, Any]] = []
    for name, value in final_globals.items():
        if name.startswith("__"):
            continue
        if isinstance(value, Graph):
            structures.append(
                {
                    "name": name,
                    "type": "graph",
                    "object_id": id(value),
                    "payload": {
                        "nodes": list(value.nodes.values()),
                        "links": list(value.links),
                    },
                }
            )
        elif isinstance(value, Heap):
            structures.append(
                {
                    "name": name,
                    "type": "heap",
                    "object_id": id(value),
                    "payload": list(value.data),
                }
            )
        elif isinstance(value, list):
            structures.append(
                {
                    "name": name,
                    "type": "list",
                    "object_id": id(value),
                    "payload": _safe_serialize(value),
                }
            )
        elif isinstance(value, dict):
            structures.append(
                {
                    "name": name,
                    "type": "dict",
                    "object_id": id(value),
                    "payload": _safe_serialize(value),
                }
            )
    return structures


def _worker_run_code(payload: Dict[str, Any], out_queue) -> None:
    code: str = payload.get("code", "")
    timeout_ms: int = int(payload.get("timeout_ms", 2000))
    max_steps: int = int(payload.get("max_steps", 50000))
    filename = "<user_code>"
    recorder = TimelineRecorder(max_steps=max_steps)

    start = time.time()
    stdout = io.StringIO()
    status = "success"
    error: Optional[str] = None

    # Provide a shim so `import networkx as nx` works even if networkx isn't installed.
    safe_builtins = _make_safe_builtins(import_overrides={"networkx": _NetworkXShim(recorder)})
    user_globals: Dict[str, Any] = {
        "__builtins__": safe_builtins,
        "Graph": lambda: Graph(_recorder=recorder),
        "Heap": lambda it=(): Heap(it, _recorder=recorder),
        "List": lambda it=(): LoggedList(it, _recorder=recorder),
        "Dict": lambda *a, **kw: LoggedDict(*a, _recorder=recorder, **kw),
    }

    try:
        compiled = compile(code, filename, "exec")
        tracer = _trace_factory(recorder, filename=filename)
        sys.settrace(tracer)
        with contextlib.redirect_stdout(stdout):
            exec(compiled, user_globals, user_globals)
    except BaseException as exc:
        status = "error"
        import traceback as _tb
        error_line = None
        frames = _tb.extract_tb(exc.__traceback__)
        for frame in reversed(frames):
            if frame.filename == filename:
                error_line = frame.lineno
                break
        error = f"{type(exc).__name__} on line {error_line}: {exc}" if error_line else f"{type(exc).__name__}: {exc}"
        recorder.emit(event="exception", line=error_line, func=None, op=error, frame=None)
    finally:
        sys.settrace(None)

    elapsed_ms = int((time.time() - start) * 1000)
    if elapsed_ms > timeout_ms:
        status = "timeout"
        error = f"Timeout after {timeout_ms}ms"

    result = {
        "status": status,
        "output": stdout.getvalue(),
        "error": error,
        "error_line": error_line,
        "timeline": [e.to_dict() for e in recorder.events],
        "timeline_states": recorder.states,
        "structures": _collect_structures(user_globals),
    }
    out_queue.put(result)


def run_code_with_timeline(code: str, *, timeout_ms: int = 2000) -> Dict[str, Any]:
    import multiprocessing

    ctx = multiprocessing.get_context("spawn")
    q = ctx.Queue()
    p = ctx.Process(target=_worker_run_code, args=({"code": code, "timeout_ms": timeout_ms}, q))
    p.daemon = True
    p.start()
    p.join(timeout_ms / 1000.0)
    if p.is_alive():
        p.terminate()
        p.join(0.25)
        return {
            "status": "timeout",
            "output": "",
            "error": f"Timeout after {timeout_ms}ms",
            "timeline": [],
            "timeline_states": [],
            "structures": [],
        }
    try:
        return q.get_nowait()
    except Exception:
        return {
            "status": "error",
            "output": "",
            "error": "No result from sandbox process",
            "timeline": [],
            "timeline_states": [],
            "structures": [],
        }


# ------------------------------
# Routes
# ------------------------------

@app.route("/")
def index():
    return "Backend up. Use POST /api/run"


@app.route("/api/run", methods=["POST"])
def run_code():
    try:
        payload = request.get_json(force=True) or {}
        code = payload.get("code", "")
        if not isinstance(code, str) or not code.strip():
            return jsonify({"status": "error", "error": "No code provided"}), 400

        result = run_code_with_timeline(code, timeout_ms=int(payload.get("timeout_ms", 2000)))

        response = {
            "status": result.get("status", "error"),
            "output": result.get("output", ""),
            "error": result.get("error"),
            "structures": result.get("structures", []),
            "timeline": result.get("timeline", []),
            "timeline_states": result.get("timeline_states", []),
        }
        return jsonify(response)
    except Exception as exc:
        return jsonify({"status": "error", "error": str(exc)}), 500


@app.route("/health")
def health():
    return {"ok": True}


# ═══════════════════════════════════════════════════════════════
#   AI CHAT & SESSION ENDPOINTS
# ═══════════════════════════════════════════════════════════════

_ai_chat = None


def _get_ai_chat():
    """Lazily create the AI chat client."""
    global _ai_chat
    if _ai_chat is None:
        from ai_orchestrator import AIChat
        _ai_chat = AIChat()
    return _ai_chat


@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    """
    Streaming AI chat endpoint.
    Accepts: { messages: [{role, content}], code?, output?, structures? }
    Returns SSE stream with text_delta, done, and error events.
    """
    from flask import stream_with_context

    payload = request.get_json(force=True)
    messages = payload.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages provided"}), 400

    try:
        chat = _get_ai_chat()
    except Exception as exc:
        def _err():
            yield f"data: {json.dumps({'type': 'error', 'error': str(exc)})}\n\n"
        return app.response_class(
            _err(),
            mimetype="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    code = payload.get("code", "")
    output = payload.get("output", "")
    structures = payload.get("structures", [])

    def generate():
        try:
            for event in chat.stream_chat(messages, code=code, output=output, structures=structures):
                yield f"data: {json.dumps(event)}\n\n"
        except Exception as stream_exc:
            yield f"data: {json.dumps({'type': 'error', 'error': str(stream_exc)})}\n\n"

    return app.response_class(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )




if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
