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
  payload: any;
  operations?: string[];
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
}
