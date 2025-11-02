from dataclasses import dataclass, field
from typing import List

from dataclasses import dataclass
from typing import Any

@dataclass
class Operation:
    name: str                # e.g. "append", "pop", "insert"
    params: list[Any] = None # e.g. [5], or ["key", "value"]

#this is the written one
@dataclass
class ErrorClass:
    name: str

@dataclass
class VariableData:
    name: str
    var_type: str
    operations: List[Operation] = field(default_factory=list)
    errors: List[ErrorClass] = field(default_factory=list)

    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return self.name == other.name