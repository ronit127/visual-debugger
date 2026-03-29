export type StructureKind = "graph" | "list" | "dict" | "heap" | "stack" | "log" | "output";

export interface BackendGraphNode {
  id: number;
  label: string;
}

export interface BackendGraphLink {
  source: number;
  target: number;
}

export interface BackendStructure {
  name: string;
  type: StructureKind;
  object_id?: number;
  payload: any;
  operations?: string[];
}

// Timeline event from sys.settrace execution
export interface TimelineEvent {
  step: number;
  ts_ms: number;
  event: "line" | "call" | "return" | "mutation" | "exception";
  line: number | null;
  func: string | null;
  var: string | null;
  object_id: number | null;
  op: string | null;
  before: any;
  after: any;
}

// Computed state at a specific timeline step (full snapshot)
export interface TimelineState {
  step: number;
  line: number | null;
  func: string | null;
  event: TimelineEvent["event"];
  structures: BackendStructure[];
}

export interface RunResponse {
  status: string;
  output: string;
  error?: string;
  graph?: {
    nodes: BackendGraphNode[];
    links: BackendGraphLink[];
  };
  graph_operations?: string[];
  structures?: BackendStructure[];
  timeline?: TimelineEvent[];
  timeline_states?: TimelineState[];
}
